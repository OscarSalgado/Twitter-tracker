# Web Dashboard Specification

## Purpose
Gives the operator a single self-hosted web page to manage tracked accounts and read the tweets that have been collected, protected from unauthenticated access.

## Requirements

### Requirement: Authenticated access
The system SHALL require HTTP Basic authentication for the dashboard and all management actions when `BASIC_AUTH_PASSWORD` is set.

#### Scenario: Request without valid credentials
- **WHEN** a request to the dashboard or a management endpoint is made without matching `BASIC_AUTH_USER`/`BASIC_AUTH_PASSWORD`
- **THEN** the system responds with 401 Unauthorized and does not perform the requested action

#### Scenario: Auth disabled
- **WHEN** `BASIC_AUTH_PASSWORD` is left empty
- **THEN** the system serves the dashboard without requiring credentials

### Requirement: Dashboard overview
The system SHALL show, on a single page, the list of tracked accounts and the most recent tweets collected across all of them.

#### Scenario: Accounts and tweets exist
- **WHEN** an authenticated operator opens the dashboard
- **THEN** the system displays tracked accounts with their status and the most recent tweets ordered newest first

### Requirement: Health check endpoint
The system SHALL expose an unauthenticated `/healthz` endpoint that reports the service is running, for use by container orchestrators.

#### Scenario: Health check requested
- **WHEN** a client requests `/healthz`
- **THEN** the system responds 200 without requiring authentication
