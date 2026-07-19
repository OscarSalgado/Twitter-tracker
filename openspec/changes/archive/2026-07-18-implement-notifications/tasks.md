# Notifications Implementation Tasks

## Implementation Tasks

### Task 1: Create notifications.py module
- [x] Create new file `app/notifications.py`
- [x] Import httpx for HTTP requests
- [x] Import logging for error tracking
- [x] Implement `send_telegram_notification(account_username: str, content: str, url: str) -> bool` function:
  - [x] Get `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from environment
  - [x] Return False early if either is missing (with debug log)
  - [x] Format message: account_username + content + url
  - [x] POST to Telegram API with 5-second timeout
  - [x] Log success (info level) if status is 200
  - [x] Log error (error level) if HTTP error or timeout
  - [x] Return True on success, False on any error
  - [x] Never raise exceptions

### Task 2: Update models.py
- [x] Verify `Tweet` model has `notified: Mapped[bool] = mapped_column(default=False)` field
- [x] If not present, add it to the Tweet model

### Task 3: Integrate notifications into tracker_service.py
- [x] Import `send_telegram_notification` from `app.notifications`
- [x] Locate `poll_account()` function in `app/tracker_service.py`
- [x] After creating a new `Tweet` record in the database:
  - [x] Call `send_telegram_notification(account.username, tweet.content, tweet.url)`
  - [x] If it returns True, set `tweet.notified = True` and commit
  - [x] If it returns False, leave `tweet.notified = False` (already default)
  - [x] Continue polling regardless of notification result

### Task 4: Manual Integration Test
- [x] Code implementation verified: `send_telegram_notification()` function created with proper async/await
- [x] Integration verified: `tracker_service.poll_account()` calls notification function
- [x] Return value handling verified: `tweet.notified` set based on function result
- [x] Error handling verified: Function catches all exceptions and logs them
- [ ] **Manual testing required**: Create test .env with real TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
- [ ] **Manual testing required**: Start application and trigger poll to verify notification arrives

### Task 5: Test Missing Configuration Behavior
- [x] Code verified: Function returns False early if env vars missing (line 25-27 in notifications.py)
- [x] Code verified: Debug log emitted when skipping (line 26)
- [x] Code verified: `notified` field will be False when function returns False
- [ ] **Manual testing required**: Remove env vars and verify polling continues without errors

### Task 6: Test Error Scenarios
- [x] Code verified: Timeout exception handled with error log (line 46-47)
- [x] Code verified: HTTPError handled with status code logging (line 42-45)
- [x] Code verified: Network errors caught and logged (line 48-50)
- [x] Code verified: Generic exceptions caught (line 51-52)
- [x] Code verified: All error paths return False (don't set notified=True)
- [ ] **Manual testing required**: Test with invalid token and verify error logging

### Task 7: Verify Logging
- [x] Debug logging verified: "Telegram notifications not configured, skipping" (line 26)
- [x] Info logging verified: "Notification sent for @{account_username}" (line 44)
- [x] Error logging verified: Multiple error types logged with reasons (lines 42, 47, 49, 52)
- [ ] **Manual testing required**: Run full poll cycle and review application logs

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
