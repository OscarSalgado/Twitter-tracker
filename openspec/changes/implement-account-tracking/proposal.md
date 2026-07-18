# Account Tracking Implementation Proposal

## What We're Building

Implement full account tracking functionality for the Twitter Tracker application, allowing operators to manage which public Twitter/X accounts this instance follows.

## Why It Matters

Account tracking is the foundation of the entire Twitter Tracker system. Without it, there are no accounts to poll for tweets. This feature enables operators to:

- Add new Twitter/X accounts to track by username
- Remove accounts they no longer wish to monitor
- View all currently tracked accounts with their status and last poll time
- Prevent duplicate accounts and handle invalid usernames gracefully

## Scope

### In Scope

- **Add tracked account** via web form with Twitter/X API resolution and deduplication
- **Remove tracked account** with complete data cleanup (including all stored tweets)
- **List tracked accounts** in the dashboard with status information (last-checked time, last error)
- **Authentication** required for all management actions when configured
- **Error handling** for invalid usernames and API failures

### Out of Scope

- Batch import/export of accounts
- Account settings or preferences
- Rate limiting for account operations
- Account search or filtering (listing is read-only)

## Risk Assessment

**No X Terms of Service concerns**: Account addition via public username resolution is standard practice. We fetch only what's already publicly available.

**No rate limit concerns**: Account resolution is a single API call per add operation; polling happens separately.

## Success Criteria

- All three requirements from the Account Tracking Specification are fully implemented
- Dashboard shows accurate account list with status
- Add/remove operations work correctly via authenticated web form
- Invalid usernames are rejected with helpful error messages
- Duplicate additions are handled gracefully (return existing instead of error)
