## 1. Test tooling

- [x] 1.1 Add `requirements-dev.txt` with `pytest`, `pytest-asyncio`,
      `pytest-cov` (dev-only, kept out of the Docker image)
- [x] 1.2 Add `pyproject.toml` with `[tool.pytest.ini_options]`
      (`addopts = "--cov=app --cov-report=term-missing"`, asyncio mode) and
      `[tool.coverage.report] fail_under = 100`
- [x] 1.3 Add `tests/conftest.py`: set `DATABASE_URL` (temp sqlite file),
      `BASIC_AUTH_PASSWORD`, and other required env vars *before* any `app.*`
      import; provide a `db_session` fixture that resets tables between tests

## 2. Unit tests per module

- [x] 2.1 `tests/test_config.py` — env var defaults and overrides
- [x] 2.2 `tests/test_database.py` — `init_db()` creates tables, `get_session()`
      returns a usable session
- [x] 2.3 `tests/test_models.py` — `Account`/`Tweet` creation, defaults
      (`utcnow`, `notified=False`), cascade delete of tweets when an account
      is deleted
- [x] 2.4 `tests/test_scraper.py` — cookie load success/missing/corrupt paths,
      missing-credentials `RuntimeError`, successful login + cookie save,
      `resolve_user`, `fetch_user_tweets` (with/without a screen name, with a
      malformed `created_at`), all against a mocked `twikit.Client`
- [x] 2.5 `tests/test_notifier.py` — no-op when Telegram isn't configured,
      successful send, and a failure that's caught and logged (mocked
      `httpx.AsyncClient`)
- [x] 2.6 `tests/test_tracker_service.py` — `add_account` (new, already
      tracked, unresolvable username), `remove_account` (existing, missing),
      `poll_account` (new tweets stored + notified, duplicate skipped, fetch
      failure recorded on the account), `poll_all_accounts` (aggregates
      across accounts)
- [x] 2.7 `tests/test_scheduler.py` — `start_scheduler` registers the
      interval job and is idempotent when called twice, `stop_scheduler` is
      a no-op when not running, using an isolated `AsyncIOScheduler` per test
- [x] 2.8 `tests/test_main.py` — `require_auth` (disabled, missing creds,
      wrong creds, correct creds), `/healthz`, dashboard render (empty and
      with accounts/tweets), `/accounts` add (success + failure), delete,
      `/check-now`, and both branches of the `lifespan` Twitter login
      try/except, all via `fastapi.testclient.TestClient`

## 3. CI enforcement

- [x] 3.1 Add `.github/workflows/tests.yml`: install
      `requirements.txt` + `requirements-dev.txt`, run `pytest`, on push and
      pull_request
- [x] 3.2 Add a `github-actions` ecosystem entry to `.github/dependabot.yml`
      (weekly), now that a workflow file exists
- [x] 3.3 Add a short "Tests y cobertura" section to `README.md`

## 4. Verify and finalize

- [x] 4.1 Run `pytest` locally and confirm coverage report shows 100% for
      `app/` with `fail_under=100` passing
- [x] 4.2 Re-run the existing manual smoke test (`uvicorn app.main:app`,
      `/healthz`, dashboard with auth) to confirm no runtime behavior changed
- [x] 4.3 `openspec validate --changes --strict` for this change
- [x] 4.4 Archive the change (`openspec archive assure-full-test-coverage`)
