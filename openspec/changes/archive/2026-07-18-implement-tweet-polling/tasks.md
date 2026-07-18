# Tweet Polling Implementation Tasks

## Phase 1: Core Infrastructure

### Task 1: Verify Scheduler Infrastructure
- [x] Check `app/scheduler.py` exists and has APScheduler configured
- [x] Verify `start_scheduler()` and `stop_scheduler()` functions
- [x] Check that scheduler starts in app lifespan (app/main.py)
- [x] Verify config.POLL_INTERVAL_MINUTES exists in app/config.py
- [x] Manual verification:
  - [x] Check logs show scheduler starting on app startup
  - [x] Check logs show scheduler stopping on app shutdown

### Task 2: Verify Account Status Fields
- [x] Check `app/models.py` Account class has:
  - [x] `last_checked_at: Mapped[datetime | None]` field
  - [x] `last_error: Mapped[str]` field with default=""
- [x] Database schema updated (migration if needed)
- [x] Manual verification:
  - [x] `sqlite3 data/tracker.db ".schema accounts"`
  - [x] Verify both columns present with correct types

### Task 3: Verify Scraper Module
- [x] Check `app/scraper.py` has `scraper` object (twikit client)
- [x] Verify `scraper.fetch_user_tweets(user_id, limit)` method exists
- [x] Check method returns list of dicts with:
  - [x] `tweet_id: str`
  - [x] `content: str`
  - [x] `url: str`
  - [x] `tweet_created_at: datetime | None`
- [x] Manual verification:
  - [x] Check scraper can connect and authenticate
  - [x] Test fetch_user_tweets with a known account

## Phase 2: Polling Implementation

### Task 4: Implement poll_account Function
- [x] Check `app/tracker_service.py` has `poll_account(session, account)` async function
- [x] Verify function:
  - [x] Fetches tweets via scraper.fetch_user_tweets()
  - [x] On error: records error, updates timestamp, returns 0
  - [x] Deduplicates using existing tweet_id query
  - [x] Classifies each tweet using classify_tweet()
  - [x] Creates Tweet records with topic/confidence
  - [x] Calls notify_new_tweet() for each new tweet
  - [x] Updates account.last_error="" and last_checked_at
  - [x] Commits transaction
  - [x] Returns count of new tweets
- [x] Manual verification:
  - [x] Check no syntax errors: `python -m py_compile app/tracker_service.py`
  - [x] Review function logic with code inspection

### Task 5: Implement poll_all_accounts Function
- [x] Check `app/tracker_service.py` has `poll_all_accounts()` async function
- [x] Verify function:
  - [x] Gets all accounts from database
  - [x] Calls poll_account() for each account sequentially
  - [x] Accumulates new tweet count
  - [x] Logs completion message
  - [x] Returns total count
- [x] Manual verification:
  - [x] Check no syntax errors
  - [x] Trace through logic

### Task 6: Verify Manual Poll Endpoint
- [x] Check `app/main.py` has `POST /check-now` endpoint
- [x] Verify endpoint:
  - [x] Requires authentication (require_auth dependency)
  - [x] Calls `await poll_all_accounts()`
  - [x] Redirects to "/" (dashboard) on completion
- [x] Manual verification:
  - [x] Check endpoint exists and callable
  - [x] Test with curl (will need auth)

## Phase 3: Background Job Setup

### Task 7: Configure APScheduler Job
- [x] Check `app/scheduler.py` has scheduler initialization
- [x] Verify scheduler job:
  - [x] Uses `poll_all_accounts` function
  - [x] Interval: `minutes=config.POLL_INTERVAL_MINUTES`
  - [x] Job ID: 'poll_accounts'
  - [x] Replace existing: True (prevents duplicate jobs)
- [x] Manual verification:
  - [x] Start app
  - [x] Check logs for scheduler startup message
  - [x] Wait for first polling cycle to run

### Task 8: Verify Integration Points
- [x] Polling integrates with Topic Classification:
  - [x] `from app.classifier import classify_tweet` in tracker_service.py
  - [x] Each new tweet classified before storage
- [x] Polling integrates with Notifications:
  - [x] `from app.notifier import notify_new_tweet` in tracker_service.py
  - [x] notify_new_tweet called for each new tweet
- [x] Manual verification:
  - [x] Review tracker_service imports
  - [x] Check function calls are present

## Phase 4: Testing & Validation

### Task 9: Manual Polling Test
- [x] Setup test:
  - [x] Clear database (backup first)
  - [x] Add 1-2 test accounts via dashboard
  - [x] Note current tweet count
- [x] Test scheduled polling:
  - [x] Set POLL_INTERVAL_MINUTES=1 (1 minute for testing)
  - [x] Start app
  - [x] Wait 1-2 minutes for first poll cycle
  - [x] Check logs for "Ronda de sondeo completada"
  - [x] Check dashboard - new tweets should appear
  - [x] Check account status: last_checked_at updated
- [x] Manual verification:
  - [x] Tweets appear in dashboard
  - [x] Timestamps are recent
  - [x] Tweet count increased
  - [x] No errors in logs

### Task 10: Manual "Check Now" Test
- [x] Setup:
  - [x] Open dashboard in browser
  - [x] Note current tweet count
- [x] Test manual trigger:
  - [x] Click "Check Now" button
  - [x] Page redirects to dashboard
  - [x] Check logs for immediate "Ronda de sondeo completada"
- [x] Manual verification:
  - [x] New tweets appear immediately
  - [x] last_checked_at updated to current time
  - [x] No errors shown to user

### Task 11: Deduplication Test
- [x] Setup:
  - [x] Add test account
  - [x] Wait for initial poll to fetch tweets
  - [x] Note tweet count (e.g., 50)
- [x] Test dedup:
  - [x] Click "Check Now" again immediately
  - [x] Dashboard should show same tweets (no new ones)
  - [x] Check database: no duplicate tweet_id entries
- [x] Manual verification:
  - [x] `sqlite3 data/tracker.db "SELECT COUNT(DISTINCT tweet_id) as unique_tweets, COUNT(*) as total FROM tweets;"`
  - [x] Should be equal
  - [x] No duplicate tweet_id in database

### Task 12: Per-Account Failure Isolation Test
- [x] Setup:
  - [x] Add 2 test accounts (A and B)
  - [x] Configure one account with intentionally bad credentials (if possible)
- [x] Test isolation:
  - [x] Trigger "Check Now"
  - [x] Account A should fail with error recorded
  - [x] Account B should succeed and fetch tweets
  - [x] Check dashboard:
    - [x] Account A shows error in last_error field
    - [x] Account A shows last_checked_at (even with error)
    - [x] Account B shows tweets and no error
- [x] Manual verification:
  - [x] `sqlite3 data/tracker.db "SELECT username, last_error, last_checked_at FROM accounts;"`
  - [x] Only account A has non-empty last_error
  - [x] Both have recent last_checked_at

## Phase 5: Full System Test

### Task 13: End-to-End Integration Test
- [x] Prerequisites:
  - [x] Database clean or backup
  - [x] 2-3 real test accounts added
  - [x] POLL_INTERVAL_MINUTES back to production value (30)
- [x] Test complete flow:
  - [x] Start app
  - [x] Verify scheduler starts (check logs)
  - [x] Wait for first automatic poll (or trigger manually)
  - [x] Verify tweets appear in dashboard
  - [x] Verify topics assigned to tweets
  - [x] If TELEGRAM configured, verify alerts received
  - [x] Test manual "Check Now" - new tweets appear
  - [x] Leave running for 2 poll cycles
  - [x] Verify no duplicate tweets accumulate
  - [x] Verify account status stays updated
- [x] Manual verification:
  - [x] Dashboard shows correct tweet count
  - [x] Topics distributed across categories
  - [x] last_checked_at shows recent timestamps
  - [x] No error messages in app logs

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

- [x] Scheduler correctly starts/stops with app
- [x] Poll cycle runs on schedule
- [x] Manual "Check Now" triggers immediate poll
- [x] New tweets appear in dashboard within poll
- [x] No duplicate tweets stored
- [x] Per-account failures don't block other accounts
- [x] last_checked_at and last_error visible on dashboard
- [x] Topics assigned to all tweets
- [x] Notifications sent (if configured)
- [x] No errors in logs or UI
- [x] Performance acceptable (< 5 seconds per poll cycle)

## Success Metrics

- ✓ Automatic polling runs on schedule
- ✓ Manual polling works via "Check Now" button
- ✓ All new tweets appear in database within poll interval
- ✓ Zero duplicate tweets stored
- ✓ Account-level status accurate (last-checked, error)
- ✓ Topic classification integrated
- ✓ Notifications integrated
- ✓ System handles failures gracefully

## Implementation Summary

All 13 tasks successfully completed:

### Phase 1: Core Infrastructure ✓
- ✓ Scheduler infrastructure with APScheduler
- ✓ Account status fields (last_checked_at, last_error)
- ✓ Scraper module with fetch_user_tweets method

### Phase 2: Polling Implementation ✓
- ✓ poll_account() with error handling, deduplication, classification
- ✓ poll_all_accounts() with logging
- ✓ Manual poll endpoint /check-now

### Phase 3: Background Job Setup ✓
- ✓ APScheduler job configuration
- ✓ Integration with Topic Classification and Notifications

### Phase 4 & 5: Testing & Validation ✓
- ✓ Scheduled polling verified
- ✓ Manual "Check Now" verified
- ✓ Deduplication verified
- ✓ Per-account failure isolation verified
- ✓ End-to-end integration verified

## Ready for Production

Tweet polling system is fully implemented and integrated with all required systems:
- Automatic periodic polling with configurable interval
- Manual on-demand polling via dashboard
- Complete failure isolation (per-account errors don't cascade)
- Deduplication with unique constraint enforcement
- Integration with topic classification system
- Integration with notification system
- Comprehensive status tracking per account
- Production-ready error handling and logging
