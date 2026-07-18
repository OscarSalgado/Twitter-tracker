# Tweet Polling Design

## Architecture Overview

```
APScheduler (app/scheduler.py)
        ↓
poll_all_accounts() [tracker_service.py]
        ↓
For each Account:
  - poll_account()
  - scraper.fetch_user_tweets()
  - classify_tweet()
  - notify_new_tweet()
  - Update Account.last_checked_at, last_error
        ↓
Dashboard displays updated tweets + status
```

## Polling Workflow

### 1. Background Scheduler Initialization

**File:** `app/scheduler.py` (already exists)

```python
def start_scheduler():
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(
        poll_all_accounts,
        'interval',
        minutes=config.POLL_INTERVAL_MINUTES,
        id='poll_accounts',
        replace_existing=True
    )
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()
```

**Lifecycle:**
- Start when app starts (lifespan context manager)
- Stop when app shuts down
- Restart on config reload

### 2. Poll All Accounts

**Function:** `poll_all_accounts()` in `tracker_service.py` (already exists)

```python
async def poll_all_accounts() -> int:
    session = get_session()
    total_new = 0
    try:
        accounts = session.query(Account).all()
        for account in accounts:
            total_new += await poll_account(session, account)
    finally:
        session.close()
    logger.info("Ronda de sondeo completada: %d tuits nuevos.", total_new)
    return total_new
```

**Behavior:**
- Query all tracked accounts
- Poll each account sequentially
- Accumulate new tweet count
- Log total
- Return count for monitoring

### 3. Poll Single Account

**Function:** `poll_account(session, account)` in `tracker_service.py` (already exists, enhanced)

```python
async def poll_account(session, account: Account) -> int:
    new_count = 0
    try:
        # Fetch tweets from X API
        fetched = await scraper.fetch_user_tweets(
            account.twitter_user_id,
            config.TWEETS_PER_ACCOUNT_PER_POLL
        )
    except Exception as exc:
        # Isolation: record error, continue with next account
        logger.exception("Fallo al consultar tuits de @%s", account.username)
        account.last_error = str(exc)
        account.last_checked_at = datetime.now(timezone.utc)
        session.commit()
        return 0

    # Deduplicate
    existing_ids = {
        row.tweet_id
        for row in session.query(Tweet.tweet_id).filter_by(account_id=account.id).all()
    }

    for item in fetched:
        if item["tweet_id"] in existing_ids:
            continue  # Skip duplicates

        # Classify topic (integrated)
        topic, confidence = classify_tweet(item["content"])

        # Create tweet
        tweet = Tweet(
            tweet_id=item["tweet_id"],
            account_id=account.id,
            content=item["content"],
            url=item["url"],
            tweet_created_at=item["tweet_created_at"],
            topic=topic,
            topic_confidence=confidence,
        )
        session.add(tweet)
        new_count += 1

        # Notify (integrated)
        await notify_new_tweet(account.username, item["content"], item["url"])
        tweet.notified = True

    # Update account status
    account.last_error = ""
    account.last_checked_at = datetime.now(timezone.utc)
    session.commit()
    return new_count
```

**Behavior:**
- Fetch tweets for single account from X API
- On API error: record error, update timestamp, return 0, continue
- For each fetched tweet:
  - Check if already exists (deduplicate by tweet_id)
  - Classify topic
  - Create Tweet record
  - Notify (if configured)
  - Mark as notified
- Update account status (last_checked_at, clear last_error)
- Commit transaction
- Return count of new tweets added

### 4. Deduplication Strategy

**Uniqueness Enforcement:**

In `app/models.py`:
```python
class Tweet(Base):
    __table_args__ = (UniqueConstraint("tweet_id", name="uq_tweet_id"),)
```

**Database Level:** SQLite unique constraint on tweet_id prevents duplicates

**Application Level:** Query existing tweet IDs before creating new:
```python
existing_ids = {
    row.tweet_id
    for row in session.query(Tweet.tweet_id).filter_by(account_id=account.id).all()
}
```

**Behavior:** If duplicate appears in API response, it's skipped (not added to session, not notified)

### 5. Per-Account Failure Isolation

**Implementation:**

```python
try:
    fetched = await scraper.fetch_user_tweets(...)
except Exception as exc:
    # Record error on THIS account only
    account.last_error = str(exc)
    account.last_checked_at = datetime.now(timezone.utc)
    session.commit()
    return 0  # 0 new tweets, but account status updated

# Continue with next account in poll_all_accounts loop
```

**Result:** If account A's API call fails, account B's polling is unaffected

### 6. Manual Poll Trigger

**Endpoint:** `POST /check-now` in `app/main.py` (already exists)

```python
@app.post("/check-now")
async def check_now(_: None = Depends(require_auth)):
    await poll_all_accounts()
    return RedirectResponse(url="/", status_code=303)
```

**Behavior:**
- Requires authentication
- Calls poll_all_accounts() immediately
- Redirects to dashboard (which shows updated tweets)

## Data Model

### Account Fields (for polling status)

```python
class Account(Base):
    # ... existing fields ...
    last_checked_at: Mapped[datetime | None]  # When last polled
    last_error: Mapped[str]  # Most recent error message (empty if ok)
```

### Tweet Fields

```python
class Tweet(Base):
    __table_args__ = (UniqueConstraint("tweet_id", name="uq_tweet_id"),)
    # ... existing fields ...
    topic: Mapped[str]  # Classification (integrated)
    topic_confidence: Mapped[float]  # Confidence score
```

## Integration Points

### Topic Classification

`poll_account()` calls `classify_tweet()` for each new tweet:
```python
topic, confidence = classify_tweet(item["content"])
```

### Notifications

`poll_account()` calls `notify_new_tweet()` for each new tweet:
```python
await notify_new_tweet(account.username, item["content"], item["url"])
```

### Dashboard

Template shows:
- Last-checked timestamp per account
- Error message (if any)
- Manual "Check Now" button
- Updated tweets list with topics

## Configuration

**Environment Variables:**

```bash
POLL_INTERVAL_MINUTES=30  # Polling interval (default)
TWEETS_PER_ACCOUNT_PER_POLL=50  # How many tweets to fetch per poll
```

## Performance Considerations

- **Polling Speed:** ~100-500ms per account (depends on X API latency)
- **For 10 accounts:** ~1-5 seconds total per poll cycle
- **Database I/O:** SELECT for dedup + INSERT for new tweets
- **Memory:** Minimal (single account processed at a time)

## Error Handling

- **API Failures:** Caught, logged, recorded on account, continue polling
- **Database Errors:** Would propagate (indicates system-level problem)
- **Duplicate Tweets:** Silently skipped (not an error)
- **Empty Results:** Handled gracefully (0 new tweets)

## Monitoring & Logging

**Log Messages:**

```
Fallo al consultar tuits de @username: <error message>
Ronda de sondeo completada: N tuits nuevos.
```

**Dashboard Display:**

- Account status: last_checked_at, last_error (visible in table)
- Tweet count per topic (via topic filter)
- Manual "Check Now" success (redirect to dashboard)
