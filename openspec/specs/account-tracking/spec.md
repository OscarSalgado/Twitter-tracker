# Account Tracking Specification

## Purpose
Lets an operator choose which public Twitter/X accounts this instance follows. Tracked accounts are the input to tweet polling: nothing is fetched or stored for an account that hasn't been added here first.

## Requirements

### Requirement: Add a tracked account
The system SHALL let an authenticated operator add a Twitter/X account to track by its username.

#### Scenario: New username is added
- **WHEN** an operator submits a username that is not already tracked
- **THEN** the system resolves the account via the Twitter/X client, stores it with its display name and internal user ID, and shows it in the tracked accounts list

#### Scenario: Username already tracked
- **WHEN** an operator submits a username that is already tracked
- **THEN** the system returns the existing account without creating a duplicate

#### Scenario: Username cannot be resolved
- **WHEN** an operator submits a username that does not exist or cannot be resolved
- **THEN** the system rejects the request with an error and does not create an account record

### Requirement: Remove a tracked account
The system SHALL let an authenticated operator stop tracking an account.

#### Scenario: Account removed
- **WHEN** an operator deletes a tracked account
- **THEN** the system removes the account and all of its stored tweets

### Requirement: List tracked accounts
The system SHALL show all currently tracked accounts, including their last poll time and last error, if any.

#### Scenario: Operator opens the dashboard
- **WHEN** an operator opens the dashboard
- **THEN** the system lists every tracked account together with its last-checked time and last error, if any
