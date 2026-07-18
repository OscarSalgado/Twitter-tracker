# Notifications Implementation Proposal

## What We're Building

Implement an optional Telegram notification system that alerts operators in real-time when new tweets are discovered and stored, without requiring them to monitor the dashboard continuously.

## Why It Matters

Tweet polling happens in the background, but operators need to know when new tweets arrive. This feature enables:

- **Real-time Awareness:** Instant alerts via Telegram when tweets arrive
- **Optional Integration:** Completely optional (no Telegram = no alerts, no errors)
- **Non-blocking:** Notification failures don't interrupt polling or lose tweets
- **Low Friction:** Simple environment variable configuration
- **Reliable Delivery:** Includes error handling and logging

## Scope

### In Scope

- **Telegram bot integration** - Send messages to configured Telegram chat
- **Optional configuration** - Works with or without TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
- **Per-tweet notifications** - Alert sent for each new tweet stored
- **Message format** - Account, content, and URL in a readable format
- **Failure isolation** - Notification errors don't stop polling
- **Error logging** - Failures logged for monitoring

### Out of Scope

- Multiple notification channels (only Telegram, not Slack, Discord, etc.)
- Notification rate limiting or batching
- Notification history/archive
- Notification preferences per account
- Custom message templates (fixed format)

## Risk Assessment

**Telegram API:** Uses httpx (already a dependency) to call Telegram Bot API - well-documented, reliable.

**Failure Handling:** Notification failures are gracefully handled - tweet is already saved, error is logged, polling continues.

**Performance:** Async HTTP request to Telegram takes ~100-500ms, non-blocking.

**Configuration:** Environment variables optional - no alerts if not configured.

## Success Criteria

- Notifications sent for all new tweets when Telegram is configured
- Notifications skipped silently when Telegram is not configured
- Notification failures logged but don't interrupt polling
- Message format is readable and informative
- Error handling is robust (timeouts, API errors, network issues)
- Configuration via TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars
