# Account Tracking Design

## Architecture Overview

The account tracking feature is built on these core components:

```
FastAPI Endpoints (/accounts) 
        ↓
tracker_service (add_account, remove_account)
        ↓
Account Model (SQLAlchemy ORM)
        ↓
SQLite Database
```

## Data Model

The `Account` model (already defined in `models.py`) stores:

```python
- id: Primary key
- username: Unique Twitter/X username (indexed for quick lookup)
- display_name: Full account name for display
- twitter_user_id: Internal X API user ID (for polling)
- added_at: Timestamp when account was added
- last_checked_at: Last time tweets were polled
- last_error: Most recent polling error (empty if no error)
- tweets: Foreign key relationship to stored tweets
```

## Implementation Strategy

### 1. Add Tracked Account

**Flow:**
1. Operator submits username via POST /accounts form
2. `add_account()` in tracker_service:
   - Strips @ and whitespace
   - Checks if account already exists (deduplication)
   - If exists, return existing account
   - If not, call `scraper.resolve_user()` to fetch user details from Twitter/X
   - Create and store new Account record
   - Return the stored account

**Error Handling:**
- Invalid/non-existent usernames: scraper raises exception → HTTP 400
- Duplicate usernames: Check existing → return 200 without creating new record

### 2. Remove Tracked Account

**Flow:**
1. Operator clicks delete button for an account
2. `remove_account()` in tracker_service:
   - Fetch account by ID
   - SQLAlchemy cascade rule automatically deletes all related tweets
   - Delete the account record
   - Commit transaction

**Data Cleanup:**
- Foreign key constraint with `cascade="all, delete-orphan"` ensures all tweets are deleted

### 3. List Tracked Accounts

**Flow:**
1. Dashboard endpoint (GET /) queries all accounts
2. Order by username for consistent display
3. Template renders account list with:
   - Username and display name
   - Last checked timestamp
   - Last error message (if any)
   - Action buttons (delete, refresh)

## Authentication

- All three operations (add, remove, list) require authentication when `BASIC_AUTH_PASSWORD` is set
- `require_auth()` dependency checks HTTP Basic credentials
- Unauthenticated requests get 401 Unauthorized
- Auth disabled if `BASIC_AUTH_PASSWORD` is empty

## API Endpoints

### POST /accounts
- **Input:** `username` form parameter (required)
- **Auth:** Required when configured
- **Response:** Redirect to dashboard (303)
- **Errors:** 400 if username invalid/cannot be resolved

### POST /accounts/{account_id}/delete
- **Input:** `account_id` path parameter
- **Auth:** Required when configured
- **Response:** Redirect to dashboard (303)
- **Side effects:** Deletes account and all its tweets

### GET /
- **Auth:** Required when configured
- **Response:** HTML dashboard with account list
- **Data:** All tracked accounts ordered by username

## Dependencies

- **scraper.resolve_user()**: Resolves Twitter/X username to user object
- **SQLAlchemy**: ORM for database operations
- **Jinja2**: Template rendering for dashboard
- **HTTPBasic**: FastAPI built-in authentication

## Key Design Decisions

1. **Deduplication on Add:** Return existing instead of error prevents accidental duplicates from retry logic
2. **Cascade Delete:** Relying on database-level cascade keeps code simple and ensures data integrity
3. **Simple Dashboard:** Minimal client-side logic; all state in database
4. **No Batch Operations:** Start simple; batch import/export can be added later if needed
