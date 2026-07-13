# Tweet Polling Specification

## Purpose
Keeps stored tweets for each tracked account up to date by periodically fetching new tweets in the background, without duplicating tweets already seen.

## Requirements

### Requirement: Periodic background polling
The system SHALL poll every tracked account on a fixed interval, configurable via `POLL_INTERVAL_MINUTES`, without requiring manual intervention.

#### Scenario: Scheduled poll runs
- **WHEN** the configured interval elapses
- **THEN** the system fetches the latest tweets for every tracked account and persists any that are new

### Requirement: Manual poll trigger
The system SHALL let an authenticated operator trigger an immediate poll of all tracked accounts outside the regular schedule.

#### Scenario: Operator requests an immediate check
- **WHEN** an operator triggers "check now"
- **THEN** the system polls all tracked accounts immediately and updates the dashboard with any new tweets

### Requirement: Deduplication of tweets
The system SHALL NOT store the same tweet twice for a given account.

#### Scenario: Tweet already stored
- **WHEN** a poll fetches a tweet whose ID already exists for that account
- **THEN** the system skips it and does not create a duplicate record

### Requirement: Per-account failure isolation
The system SHALL record a poll failure against the specific account that failed without stopping polling of the other tracked accounts.

#### Scenario: One account fails to fetch
- **WHEN** fetching tweets for one tracked account raises an error
- **THEN** the system records the error message and last-checked time on that account and continues polling the remaining accounts
