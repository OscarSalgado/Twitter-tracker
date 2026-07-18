# Account Tracking Implementation Tasks

## Verification Tasks

### Task 1: Verify Account Model
- [ ] Check `app/models.py` has Account class with all required fields:
  - username (unique, indexed)
  - display_name
  - twitter_user_id
  - last_checked_at
  - last_error
  - Cascade delete relationship to tweets
- [ ] Database schema matches spec (run migrations if needed)
- [ ] Manual verification: Start app, check database schema with `sqlite3 data/tracker.db ".schema accounts"`

### Task 2: Verify add_account Service
- [ ] Check `app/tracker_service.py` has add_account() function
- [ ] Verifies it accepts username string
- [ ] Handles username normalization (strip, lstrip @)
- [ ] Checks for existing account (deduplication)
- [ ] Calls scraper.resolve_user() to fetch user details
- [ ] Creates Account with username, display_name, twitter_user_id
- [ ] Returns the stored account
- [ ] Manual verification:
  - Start app with uvicorn
  - Add a real public account via form (e.g., @elonmusk)
  - Verify it appears in dashboard
  - Try adding again; verify it returns same account (no duplicate)
  - Add invalid username; verify error message appears

### Task 3: Verify remove_account Service
- [ ] Check `app/tracker_service.py` has remove_account(account_id) function
- [ ] Fetches account by ID
- [ ] Deletes account (cascade deletes tweets automatically)
- [ ] Manual verification:
  - Start app
  - Add an account
  - Delete it via dashboard button
  - Verify it's gone from list
  - Verify its tweets are also deleted: `sqlite3 data/tracker.db "SELECT COUNT(*) FROM tweets WHERE account_id=<deleted-id>"`

### Task 4: Verify API Endpoints
- [ ] Check `app/main.py` has:
  - POST /accounts endpoint with username form parameter
  - POST /accounts/{account_id}/delete endpoint
  - GET / dashboard endpoint
- [ ] All endpoints use require_auth() when configured
- [ ] Add redirects to dashboard on success
- [ ] Manual verification:
  - Start app with `BASIC_AUTH_PASSWORD=test123` in .env
  - Try accessing dashboard without auth → 401 Unauthorized
  - Access with auth → dashboard appears
  - Try posting to /accounts without auth → 401
  - Add account with auth → redirects to dashboard, account appears
  - Try deleting with invalid account_id → verify graceful handling

### Task 5: Verify Dashboard Display
- [ ] Check `app/templates/index.html` renders:
  - List of all accounts
  - Username and display name for each
  - Last checked timestamp (if any)
  - Last error message (if any)
  - Delete button for each account
  - Form to add new account with username input
- [ ] Check template shows accurate status (last_checked_at, last_error fields)
- [ ] Manual verification:
  - Start app
  - Add 2-3 accounts
  - Dashboard shows all with correct info
  - Run a poll (via "Check now" button)
  - last_checked_at updates for all accounts
  - If poll fails on one, last_error shows only for that account

### Task 6: Verify Error Handling
- [ ] Invalid username (e.g., @nonexistentuser12345):
  - [ ] scraper.resolve_user() raises exception
  - [ ] add_account() propagates exception
  - [ ] Endpoint catches and returns 400 with error message
  - [ ] Dashboard shows error, user can retry
- [ ] Duplicate username:
  - [ ] add_account() detects via query
  - [ ] Returns existing account without creating new
  - [ ] No database errors, no duplicates in dashboard
- [ ] Non-existent account_id in delete:
  - [ ] remove_account() handles gracefully
  - [ ] No database errors
  - [ ] Redirect to dashboard succeeds

## Final Verification Steps

### Step 1: Start the Application
```bash
docker-compose up
# OR
uvicorn app.main:app --reload
```

### Step 2: Test Complete Flow
1. Open dashboard at http://localhost:8000
2. Add a real public account (e.g., @AnthropicAI)
   - Verify account appears in list with correct display name and user ID
3. Try adding invalid account (e.g., @zzz_nonexistent_zzz)
   - Verify error appears
4. Add another real account
   - Verify list now has 2 accounts
5. Trigger manual poll ("Check now" button)
   - Verify both accounts show updated last_checked_at
6. Delete one account
   - Verify it's gone from list
   - Verify dashboard only shows remaining account
7. If auth configured, test auth:
   - Close browser (clear cookies)
   - Try accessing dashboard without credentials
   - Verify 401 challenge
   - Enter credentials
   - Verify dashboard appears

### Step 3: Verify Data Integrity
```bash
# Check accounts table
sqlite3 data/tracker.db "SELECT username, display_name, last_checked_at, last_error FROM accounts ORDER BY username;"

# Check a deleted account's tweets are gone
sqlite3 data/tracker.db "SELECT COUNT(*) FROM tweets WHERE account_id=<some-id>;"
```

## Definition of Done

- [ ] All verification tasks completed with manual testing
- [ ] Dashboard displays accurate account list and status
- [ ] Add/remove operations work via web form
- [ ] Invalid usernames rejected with helpful messages
- [ ] Duplicate additions handled gracefully
- [ ] Authentication enforced when configured
- [ ] Error messages are user-friendly and in project's language convention
- [ ] No database errors or orphaned data
