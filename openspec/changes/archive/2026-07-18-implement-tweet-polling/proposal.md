# Tweet Polling Implementation Proposal

## What We're Building

Implement a robust tweet polling system that automatically and continuously fetches new tweets from tracked accounts on a configurable interval, stores them without duplication, and allows manual polling on-demand via the dashboard.

## Why It Matters

Tweet polling is the **core functionality** of Twitter Tracker. Without it, the application simply stores an empty database. This feature enables:

- **Automatic Updates:** Continuously fresh tweets from tracked accounts
- **Background Operation:** Polling runs on a schedule without user intervention
- **Manual Control:** Operators can trigger immediate polling when needed
- **Data Integrity:** No duplicate tweets, even with concurrent updates
- **Fault Isolation:** One account's failure doesn't block polling of others
- **Transparency:** Last-checked timestamps and error logging per account

## Scope

### In Scope

- **Periodic background polling** on configurable interval (POLL_INTERVAL_MINUTES)
- **Manual poll trigger** via "Check Now" button on dashboard
- **Tweet deduplication** - prevent storing same tweet twice
- **Per-account failure isolation** - errors don't cascade
- **Status tracking** - last_checked_at and last_error on Account model
- **Topic classification** integration (uses Topic Classification system)
- **Notifications** integration (sends Telegram alerts for new tweets)

### Out of Scope

- Backfill historical tweets (only fetch new since last poll)
- Advanced scheduling (e.g., different intervals per account)
- Rate limit handling (assume X API respects rate limits)
- Retry logic on transient failures (fail-fast per account)
- Polling pause/suspend per account

## Risk Assessment

**X Terms of Service:** Polling public tweets via official API fully complies with ToS.

**Rate Limits:** X API has generous rate limits; polling every 30 minutes well within limits.

**Data Growth:** Tweet storage grows linearly with time and account count; SQLite handles millions.

**Background Task:** APScheduler is production-proven for this use case.

## Success Criteria

- Background polling runs on schedule without manual intervention
- Manual "Check Now" triggers immediate poll and updates dashboard
- New tweets appear in dashboard within poll interval
- Duplicate tweets never stored (tweet_id uniqueness enforced)
- One account's API failure doesn't block polling of others
- Last-checked timestamp and error status visible per account
- Poll duration acceptable (< 5 seconds for 10 accounts)
