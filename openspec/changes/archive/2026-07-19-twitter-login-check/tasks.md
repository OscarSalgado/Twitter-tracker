## 1. Expose scraper login state

- [x] 1.1 Add `is_logged_in` (bool) and `last_login_error` (str | None) to `TwitterScraper` in `app/scraper.py`, updated on both successful and failed `login()` calls
- [x] 1.2 Make `login()` safely re-callable (it already sets `self._logged_in = True` only on success; ensure a failed attempt records the error without leaving stale state)

## 2. Retry login before polling

- [x] 2.1 In `app/tracker_service.py`, at the start of `poll_all_accounts()`, call `scraper.login()` again if `not scraper.is_logged_in`, wrapped in try/except so a failure just skips this poll cycle
- [x] 2.2 On retry failure, log the error and return early (0 new tweets) without touching account records

## 3. Surface status via /healthz and dashboard

- [x] 3.1 Update `/healthz` in `app/main.py` to include a `twitter_login` field (`"ok"` or `"error"`) based on `scraper.is_logged_in`, keeping the HTTP status code 200
- [x] 3.2 Pass `scraper.is_logged_in` / `scraper.last_login_error` into the `dashboard()` route's template context
- [x] 3.3 Add a warning banner in `app/templates/index.html` shown when not logged in, using the existing plain-CSS styling

## 4. Sync specs and verify

- [x] 4.1 Sync the `web-dashboard` and `tweet-polling` delta specs into `openspec/specs/web-dashboard/spec.md` and `openspec/specs/tweet-polling/spec.md`
- [x] 4.2 Run `openspec validate twitter-login-check --strict` to confirm the change's artifacts are well-formed
- [x] 4.3 Start the app with `uvicorn app.main:app` (valid and, separately, deliberately broken credentials) and manually verify: `/healthz` reflects login state, the dashboard banner appears/disappears correctly, and a poll cycle retries login when previously failed
