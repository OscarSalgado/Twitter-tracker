# Notifications Specification

## Purpose
Optionally pushes an alert to Telegram whenever a new tweet is discovered, so operators don't have to keep the dashboard open to notice new activity.

## Requirements

### Requirement: Telegram notification on new tweet
The system SHALL send a Telegram message containing the account, tweet content, and tweet URL whenever a new tweet is stored, if Telegram is configured.

#### Scenario: Telegram is configured
- **WHEN** a new tweet is stored and `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are both set
- **THEN** the system sends a message to that chat with the tweet's account, content, and URL

### Requirement: Notifications are optional
The system SHALL skip sending notifications, without failing the poll, when Telegram is not configured.

#### Scenario: Telegram is not configured
- **WHEN** a new tweet is stored and `TELEGRAM_BOT_TOKEN` or `TELEGRAM_CHAT_ID` is missing
- **THEN** the system stores the tweet normally and does not attempt to send a notification

### Requirement: Notification failures do not break polling
The system SHALL log a notification delivery failure without interrupting the current poll or losing the stored tweet.

#### Scenario: Telegram API call fails
- **WHEN** the Telegram API request errors or times out
- **THEN** the system logs the failure and continues processing the remaining tweets in that poll
