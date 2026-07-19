## MODIFIED Requirements

### Requirement: Health check endpoint
The system SHALL expose an unauthenticated `/healthz` endpoint that reports the service is running, for use by container orchestrators, and that also reports whether the Twitter/X login is currently active.

#### Scenario: Health check requested
- **WHEN** a client requests `/healthz`
- **THEN** the system responds 200 without requiring authentication

#### Scenario: Twitter login is active
- **WHEN** the scraper is currently logged in to Twitter/X
- **THEN** the `/healthz` response indicates the Twitter login status is healthy

#### Scenario: Twitter login has failed
- **WHEN** the scraper is not currently logged in to Twitter/X
- **THEN** the `/healthz` response indicates the Twitter login status is unhealthy

### Requirement: Dashboard overview
The system SHALL show, on a single page, the list of tracked accounts and the most recent tweets collected across all of them, and SHALL warn the operator when the Twitter/X login is not currently active.

#### Scenario: Accounts and tweets exist
- **WHEN** an authenticated operator opens the dashboard
- **THEN** the system displays tracked accounts with their status and the most recent tweets ordered newest first

#### Scenario: Twitter login is not active
- **WHEN** an authenticated operator opens the dashboard while the scraper is not logged in to Twitter/X
- **THEN** the system displays a visible warning that tracking is currently broken
