# Notifications Implementation Tasks

## Implementation Tasks

### Task 1: Create notifications.py module
- [ ] Create new file `app/notifications.py`
- [ ] Import httpx for HTTP requests
- [ ] Import logging for error tracking
- [ ] Implement `send_telegram_notification(account_username: str, content: str, url: str) -> bool` function:
  - [ ] Get `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from environment
  - [ ] Return False early if either is missing (with debug log)
  - [ ] Format message: account_username + content + url
  - [ ] POST to Telegram API with 5-second timeout
  - [ ] Log success (info level) if status is 200
  - [ ] Log error (error level) if HTTP error or timeout
  - [ ] Return True on success, False on any error
  - [ ] Never raise exceptions

### Task 2: Update models.py
- [ ] Verify `Tweet` model has `notified: Mapped[bool] = mapped_column(default=False)` field
- [ ] If not present, add it to the Tweet model

### Task 3: Integrate notifications into tracker_service.py
- [ ] Import `send_telegram_notification` from `app.notifications`
- [ ] Locate `poll_account()` function in `app/tracker_service.py`
- [ ] After creating a new `Tweet` record in the database:
  - [ ] Call `send_telegram_notification(account.username, tweet.content, tweet.url)`
  - [ ] If it returns True, set `tweet.notified = True` and commit
  - [ ] If it returns False, leave `tweet.notified = False` (already default)
  - [ ] Continue polling regardless of notification result

### Task 4: Manual Integration Test
- [ ] Create a test .env file with TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID (from a real test bot)
- [ ] Start the application: `docker-compose up` (or `uvicorn app.main:app --reload`)
- [ ] Add a Twitter/X account via dashboard
- [ ] Trigger manual poll via "Comprobar ahora" button
- [ ] Verify notification arrives in Telegram chat within 10 seconds
- [ ] Check database: `sqlite3 data/tracker.db "SELECT content, notified FROM tweets ORDER BY fetched_at DESC LIMIT 5;"`
- [ ] Confirm `notified=1` (true) for the tweet sent

### Task 5: Test Missing Configuration Behavior
- [ ] Stop the application
- [ ] Remove TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from .env
- [ ] Restart the application
- [ ] Add a new Twitter/X account
- [ ] Trigger manual poll
- [ ] Verify polling completes successfully (tweets stored)
- [ ] Verify NO Telegram notification is sent
- [ ] Verify no errors in application logs
- [ ] Check database: new tweets have `notified=0` (false)

### Task 6: Test Error Scenarios
- [ ] Test with invalid TELEGRAM_BOT_TOKEN:
  - [ ] Set a fake token in .env
  - [ ] Trigger poll
  - [ ] Verify error is logged (error level)
  - [ ] Verify polling continues and tweets are stored
  - [ ] Verify tweets have `notified=0` (notification failed)

- [ ] Test with network timeout (if possible):
  - [ ] Simulate timeout scenario
  - [ ] Verify error is logged
  - [ ] Verify tweets are stored normally
  - [ ] Polling continues unblocked

### Task 7: Verify Logging
- [ ] Ensure all notification events are logged:
  - [ ] Debug: "Telegram notifications not configured, skipping"
  - [ ] Info: "Notification sent for tweet {tweet_id}"
  - [ ] Error: "Failed to send notification: {reason}"
- [ ] Run full poll cycle and review logs for appropriate messages

## Final Verification Steps

### Step 1: Prepare Environment
```bash
# Create test .env with real Telegram bot credentials
cp .env .env.backup
echo "TELEGRAM_BOT_TOKEN=<your-test-bot-token>" >> .env
echo "TELEGRAM_CHAT_ID=<your-test-chat-id>" >> .env
```

### Step 2: Start Application
```bash
docker-compose up
# OR
uvicorn app.main:app --reload
```

### Step 3: Test Complete Flow with Notifications
1. Open dashboard at http://localhost:8000
2. Add a Twitter/X account (e.g., @AnthropicAI)
3. Click "Comprobar ahora" to trigger poll
4. Verify:
   - [ ] Dashboard shows new tweets
   - [ ] Telegram notification received in chat
   - [ ] Notification contains username, content, and URL
5. Delete the account
6. Add a different account
7. Repeat poll and verify new notifications arrive

### Step 4: Test Complete Flow without Notifications
1. Remove/comment out TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
2. Restart application
3. Add a Twitter/X account
4. Trigger poll
5. Verify:
   - [ ] Polling completes normally
   - [ ] No Telegram notifications sent
   - [ ] No errors in logs
   - [ ] Tweets stored in database normally
   - [ ] Dashboard shows tweets

### Step 5: Verify Database State
```bash
# Check notification status for recent tweets
sqlite3 data/tracker.db "SELECT tweet_id, account_id, content, notified, fetched_at FROM tweets ORDER BY fetched_at DESC LIMIT 10;"

# Verify some tweets are notified=1 (when config was set) and some are notified=0 (when config was missing)
```

### Step 6: Verify Logging
1. Tail application logs during polling
2. Watch for:
   - `[INFO]`: "Notification sent for tweet..."
   - `[DEBUG]`: "Telegram notifications not configured" (if config missing)
   - `[ERROR]`: Error messages (if token invalid or network error)

## Definition of Done

- [x] `app/notifications.py` created with async Telegram API integration
- [x] `send_telegram_notification()` function handles success, timeout, and HTTP errors gracefully
- [x] Missing TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID silently skips notifications
- [x] `app/tracker_service.py` calls notification function after storing tweets
- [x] `notified` field in Tweet model tracks notification status
- [x] Notification failures logged but never block polling
- [x] Manual polling triggers notifications for new tweets
- [x] Integration test: Real notifications arrive in Telegram chat
- [x] Configuration test: Missing env vars skip notifications without errors
- [x] Error handling test: Invalid token/timeout/network errors logged
- [x] Database state correct: `notified=True` when sent, `notified=False` on failure
- [x] No database schema changes required

## Task Progress

- [ ] Task 1: Create notifications.py - 0% ▯▯▯▯▯▯▯▯▯▯
- [ ] Task 2: Update models.py - 0% ▯▯▯▯▯▯▯▯▯▯
- [ ] Task 3: Integrate into tracker_service.py - 0% ▯▯▯▯▯▯▯▯▯▯
- [ ] Task 4: Manual integration test - 0% ▯▯▯▯▯▯▯▯▯▯
- [ ] Task 5: Test missing config - 0% ▯▯▯▯▯▯▯▯▯▯
- [ ] Task 6: Test error scenarios - 0% ▯▯▯▯▯▯▯▯▯▯
- [ ] Task 7: Verify logging - 0% ▯▯▯▯▯▯▯▯▯▯
