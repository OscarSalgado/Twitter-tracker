# Notifications Design

## Architecture Overview

The Telegram notification system extends the tweet polling workflow with optional push notifications:

```
poll_account() in tracker_service
        ↓
Tweet created and saved
        ↓
send_telegram_notification() 
        ↓
Telegram Bot API
        ↓
Operator's Telegram chat
```

## Data Model

The `Tweet` model already has the `notified` field (boolean, default=False):

```python
notified: Mapped[bool] = mapped_column(default=False)
```

This tracks whether a notification has been sent for each tweet, enabling:
- Preventing duplicate notifications on retry
- Selective re-notification if needed
- Audit trail of notification history

## Implementation Strategy

### 1. Telegram Bot Integration

**Setup (one-time, before deployment):**
1. Create a Telegram Bot via BotFather (@BotFather on Telegram)
2. Get the bot token
3. Start a chat with the bot
4. Get the chat ID (can be extracted from first message)
5. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in environment

**Send Notification Function:**
- Location: `app/notifications.py` (new file)
- Function: `send_telegram_notification(account_username: str, content: str, url: str) -> bool`
- HTTP POST to `https://api.telegram.org/bot{token}/sendMessage`
- Request body: `{"chat_id": chat_id, "text": formatted_message}`
- Returns True on success, False on failure
- Logs errors without raising exceptions

### 2. Message Format

The Telegram message format:

```
@<account_username>
<tweet_content>
<URL>
```

Example:
```
@elonmusk
This is a sample tweet about innovation in technology
https://x.com/elonmusk/status/123456789
```

### 3. Trigger on Tweet Creation

**Location:** `app/tracker_service.py`, in the `poll_account()` function

**Flow:**
1. After creating a new Tweet record
2. Mark `notified=False` initially (when creating)
3. Call `send_telegram_notification()` with tweet details
4. If successful, update `notified=True`
5. If fails, leave `notified=False` (can retry later)
6. Continue polling even if notification fails

### 4. Optional Configuration

**Behavior:**
- If `TELEGRAM_BOT_TOKEN` is not set → skip all notification logic
- If `TELEGRAM_CHAT_ID` is not set → skip all notification logic
- If both set → send notifications for each new tweet
- Logs a debug message when skipping due to missing config

**Error Handling:**
- Timeout: 5 seconds per request
- HTTP errors (e.g., invalid token): Logged, polling continues
- Network errors: Logged, polling continues
- Message format errors: Logged, polling continues
- Never blocks or interrupts polling

### 5. Logging

**Log locations:**
- `logging.debug()` for skipped notifications (no config)
- `logging.info()` for successful notification sends
- `logging.error()` for failed sends with reason (timeout, HTTP error, etc.)

## Database

No schema changes needed. The `notified` field already exists in the `Tweet` model.

## API Endpoints

No new endpoints are added. Notification sending is internal to the polling service.

## Configuration

### Environment Variables

```
TELEGRAM_BOT_TOKEN=<token-from-botfather>
TELEGRAM_CHAT_ID=<numeric-chat-id>
```

Both optional. If either is missing, notifications are silently skipped.

### Default Behavior (no config)

```
$ cat .env
BASIC_AUTH_PASSWORD=test

# No TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID set
```

App runs normally, polling works, no notifications sent, no errors.

## Dependencies

- **httpx** (already installed): async HTTP client for Telegram API calls
- **logging** (built-in): for error tracking and audit logs

## Key Design Decisions

1. **Async HTTP with httpx:** Non-blocking, matches FastAPI's async pattern, already a dependency
2. **Graceful Degradation:** Missing config means no notifications, not an error
3. **Failure Isolation:** Notification failures never block tweet polling or storage
4. **No Rate Limiting:** First version sends per-tweet; can batch later if needed
5. **Logging-Based Audit:** `notified` field + logs provide full visibility
6. **No Persistence of Failures:** Failed sends aren't queued; next run retries naturally via `notified=False`

## Testing Strategy

Manual testing:
1. Set up real Telegram bot and get token
2. Create .env with `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
3. Add a Twitter account
4. Trigger polling
5. Verify notification arrives in Telegram chat
6. Check `notified` field in database for that tweet

Integration testing:
1. Test with missing `TELEGRAM_BOT_TOKEN` → no errors, notification skipped
2. Test with invalid token → error logged, polling continues
3. Test with network timeout → error logged, polling continues
4. Test duplicate notification prevention via `notified` flag
