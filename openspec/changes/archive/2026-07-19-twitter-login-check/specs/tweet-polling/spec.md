## ADDED Requirements

### Requirement: Login retry before polling
The system SHALL attempt to log in to Twitter/X before a poll (scheduled or manually triggered) if it is not currently logged in, instead of requiring a process restart to recover from a login failure.

#### Scenario: Not logged in when a poll starts
- **WHEN** a scheduled or manual poll begins and the scraper is not currently logged in
- **THEN** the system attempts to log in again before fetching tweets for any account

#### Scenario: Retry login succeeds
- **WHEN** the retried login attempt succeeds
- **THEN** the poll proceeds to fetch tweets for tracked accounts as normal

#### Scenario: Retry login fails
- **WHEN** the retried login attempt fails
- **THEN** the system records the login error, skips fetching tweets for this poll cycle, and does not crash the scheduler
