# Tweet Polling Implementation Tasks

## Phase 1: Core Infrastructure

### Task 1: Verify Scheduler Infrastructure
- [ ] Check `app/scheduler.py` exists and has APScheduler configured
- [ ] Verify `start_scheduler()` and `stop_scheduler()` functions
- [ ] Check that scheduler starts in app lifespan (app/main.py)
- [ ] Verify config.POLL_INTERVAL_MINUTES exists in app/config.py
- [ ] Manual verification:
  - [ ] Check logs show scheduler starting on app startup
  - [ ] Check logs show scheduler stopping on app shutdown

### Task 2: Verify Account Status Fields
- [ ] Check `app/models.py` Account class has:
  - [ ] `last_checked_at: Mapped[datetime | None]` field
  - [ ] `last_error: Mapped[str]` field with default=""
- [ ] Database schema updated (migration if needed)
- [ ] Manual verification:
  - [ ] `sqlite3 data/tracker.db ".schema accounts"`
  - [ ] Verify both columns present with correct types

### Task 3: Verify Scraper Module
- [ ] Check `app/scraper.py` has `scraper` object (twikit client)
- [ ] Verify `scraper.fetch_user_tweets(user_id, limit)` method exists
- [ ] Check method returns list of dicts with:
  - [ ] `tweet_id: str`
  - [ ] `content: str`
  - [ ] `url: str`
  - [ ] `tweet_created_at: datetime | None`
- [ ] Manual verification:
  - [ ] Check scraper can connect and authenticate
  - [ ] Test fetch_user_tweets with a known account

## Phase 2: Polling Implementation

### Task 4: Implement poll_account Function
- [ ] Check `app/tracker_service.py` has `poll_account(session, account)` async function
- [ ] Verify function:
  - [ ] Fetches tweets via scraper.fetch_user_tweets()
  - [ ] On error: records error, updates timestamp, returns 0
  - [ ] Deduplicates using existing tweet_id query
  - [ ] Classifies each tweet using classify_tweet()
  - [ ] Creates Tweet records with topic/confidence
  - [ ] Calls notify_new_tweet() for each new tweet
  - [ ] Updates account.last_error="" and last_checked_at
  - [ ] Commits transaction
  - [ ] Returns count of new tweets
- [ ] Manual verification:
  - [ ] Check no syntax errors: `python -m py_compile app/tracker_service.py`
  - [ ] Review function logic with code inspection

### Task 5: Implement poll_all_accounts Function
- [ ] Check `app/tracker_service.py` has `poll_all_accounts()` async function
- [ ] Verify function:
  - [ ] Gets all accounts from database
  - [ ] Calls poll_account() for each account sequentially
  - [ ] Accumulates new tweet count
  - [ ] Logs completion message
  - [ ] Returns total count
- [ ] Manual verification:
  - [ ] Check no syntax errors
  - [ ] Trace through logic

### Task 6: Verify Manual Poll Endpoint
- [ ] Check `app/main.py` has `POST /check-now` endpoint
- [ ] Verify endpoint:
  - [ ] Requires authentication (require_auth dependency)
  - [ ] Calls `await poll_all_accounts()`
  - [ ] Redirects to "/" (dashboard) on completion
- [ ] Manual verification:
  - [ ] Check endpoint exists and callable
  - [ ] Test with curl (will need auth)

## Phase 3: Background Job Setup

### Task 7: Configure APScheduler Job
- [ ] Check `app/scheduler.py` has scheduler initialization
- [ ] Verify scheduler job:
  - [ ] Uses `poll_all_accounts` function
  - [ ] Interval: `minutes=config.POLL_INTERVAL_MINUTES`
  - [ ] Job ID: 'poll_accounts'
  - [ ] Replace existing: True (prevents duplicate jobs)
- [ ] Manual verification:
  - [ ] Start app
  - [ ] Check logs for scheduler startup message
  - [ ] Wait for first polling cycle to run

### Task 8: Verify Integration Points
- [ ] Polling integrates with Topic Classification:
  - [ ] `from app.classifier import classify_tweet` in tracker_service.py
  - [ ] Each new tweet classified before storage
- [ ] Polling integrates with Notifications:
  - [ ] `from app.notifier import notify_new_tweet` in tracker_service.py
  - [ ] notify_new_tweet called for each new tweet
- [ ] Manual verification:
  - [ ] Review tracker_service imports
  - [ ] Check function calls are present

## Phase 4: Testing & Validation

### Task 9: Manual Polling Test
- [ ] Setup test:
  - [ ] Clear database (backup first)
  - [ ] Add 1-2 test accounts via dashboard
  - [ ] Note current tweet count
- [ ] Test scheduled polling:
  - [ ] Set POLL_INTERVAL_MINUTES=1 (1 minute for testing)
  - [ ] Start app
  - [ ] Wait 1-2 minutes for first poll cycle
  - [ ] Check logs for "Ronda de sondeo completada"
  - [ ] Check dashboard - new tweets should appear
  - [ ] Check account status: last_checked_at updated
- [ ] Manual verification:
  - [ ] Tweets appear in dashboard
  - [ ] Timestamps are recent
  - [ ] Tweet count increased
  - [ ] No errors in logs

### Task 10: Manual "Check Now" Test
- [ ] Setup:
  - [ ] Open dashboard in browser
  - [ ] Note current tweet count
- [ ] Test manual trigger:
  - [ ] Click "Check Now" button
  - [ ] Page redirects to dashboard
  - [ ] Check logs for immediate "Ronda de sondeo completada"
- [ ] Manual verification:
  - [ ] New tweets appear immediately
  - [ ] last_checked_at updated to current time
  - [ ] No errors shown to user

### Task 11: Deduplication Test
- [ ] Setup:
  - [ ] Add test account
  - [ ] Wait for initial poll to fetch tweets
  - [ ] Note tweet count (e.g., 50)
- [ ] Test dedup:
  - [ ] Click "Check Now" again immediately
  - [ ] Dashboard should show same tweets (no new ones)
  - [ ] Check database: no duplicate tweet_id entries
- [ ] Manual verification:
  - [ ] `sqlite3 data/tracker.db "SELECT COUNT(DISTINCT tweet_id) as unique_tweets, COUNT(*) as total FROM tweets;"`
  - [ ] Should be equal
  - [ ] No duplicate tweet_id in database

### Task 12: Per-Account Failure Isolation Test
- [ ] Setup:
  - [ ] Add 2 test accounts (A and B)
  - [ ] Configure one account with intentionally bad credentials (if possible)
- [ ] Test isolation:
  - [ ] Trigger "Check Now"
  - [ ] Account A should fail with error recorded
  - [ ] Account B should succeed and fetch tweets
  - [ ] Check dashboard:
    - [ ] Account A shows error in last_error field
    - [ ] Account A shows last_checked_at (even with error)
    - [ ] Account B shows tweets and no error
- [ ] Manual verification:
  - [ ] `sqlite3 data/tracker.db "SELECT username, last_error, last_checked_at FROM accounts;"`
  - [ ] Only account A has non-empty last_error
  - [ ] Both have recent last_checked_at

## Phase 5: Full System Test

### Task 13: End-to-End Integration Test
- [ ] Prerequisites:
  - [ ] Database clean or backup
  - [ ] 2-3 real test accounts added
  - [ ] POLL_INTERVAL_MINUTES back to production value (30)
- [ ] Test complete flow:
  - [ ] Start app
  - [ ] Verify scheduler starts (check logs)
  - [ ] Wait for first automatic poll (or trigger manually)
  - [ ] Verify tweets appear in dashboard
  - [ ] Verify topics assigned to tweets
  - [ ] If TELEGRAM configured, verify alerts received
  - [ ] Test manual "Check Now" - new tweets appear
  - [ ] Leave running for 2 poll cycles
  - [ ] Verify no duplicate tweets accumulate
  - [ ] Verify account status stays updated
- [ ] Manual verification:
  - [ ] Dashboard shows correct tweet count
  - [ ] Topics distributed across categories
  - [ ] last_checked_at shows recent timestamps
  - [ ] No error messages in app logs

## Final Verification Steps

### Clean Database Test
```bash
# If testing with clean database
sqlite3 data/tracker.db "DELETE FROM tweets;"
```

### Start Fresh App Instance
```bash
docker-compose up  # or uvicorn
```

### Check Polling Kicks Off
```bash
# Monitor logs
docker-compose logs -f
# Should see: "Ronda de sondeo completada: N tuits nuevos" after POLL_INTERVAL_MINUTES
```

### Verify Data Integrity
```bash
# Check all tweets have unique tweet_id
sqlite3 data/tracker.db "SELECT COUNT(DISTINCT tweet_id), COUNT(*) FROM tweets;"

# Check no tweets have NULL topic
sqlite3 data/tracker.db "SELECT COUNT(*) FROM tweets WHERE topic IS NULL;"  # Should be 0

# Check all accounts have last_checked_at (if polled)
sqlite3 data/tracker.db "SELECT COUNT(*) FROM accounts WHERE last_checked_at IS NULL;"
```

## Definition of Done

- [ ] Scheduler correctly starts/stops with app
- [ ] Poll cycle runs on schedule
- [ ] Manual "Check Now" triggers immediate poll
- [ ] New tweets appear in dashboard within poll
- [ ] No duplicate tweets stored
- [ ] Per-account failures don't block other accounts
- [ ] last_checked_at and last_error visible on dashboard
- [ ] Topics assigned to all tweets
- [ ] Notifications sent (if configured)
- [ ] No errors in logs or UI
- [ ] Performance acceptable (< 5 seconds per poll cycle)

## Success Metrics

- ✓ Automatic polling runs on schedule
- ✓ Manual polling works via "Check Now" button
- ✓ All new tweets appear in database within poll interval
- ✓ Zero duplicate tweets stored
- ✓ Account-level status accurate (last-checked, error)
- ✓ Topic classification integrated
- ✓ Notifications integrated
- ✓ System handles failures gracefully
