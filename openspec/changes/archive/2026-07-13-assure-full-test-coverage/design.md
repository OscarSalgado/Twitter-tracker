## Context

`app/` is ~420 lines across 8 modules (config, database, models, scraper,
notifier, tracker_service, scheduler, main) with zero automated tests today.
Everything has been verified by hand (`uvicorn` + `curl`). The app talks to
two external services that must never be hit in a test run: Twitter/X (via
`twikit`) and Telegram (via `httpx`).

## Goals / Non-Goals

**Goals:**
- 100% **line** coverage of `app/`, enforced by `pytest-cov`'s
  `--cov-fail-under=100` both locally and in CI.
- Zero real network calls in tests — `twikit.Client` and `httpx` are always
  mocked; tests must pass with no Twitter/Telegram credentials and no
  network access.
- Tests run against a throwaway SQLite file per test session, never against
  `data/tracker.db`.

**Non-Goals:**
- Branch coverage. Line coverage is the enforced bar; a ternary like
  `database.py`'s `check_same_thread` selection is fully line-covered
  regardless of which branch it takes, and that's sufficient here.
- End-to-end tests against real Twitter/Telegram accounts. Out of scope —
  those would violate the "no real network" goal and need real secrets.
- Rewriting app code for testability beyond trivial, behavior-preserving
  changes (if any are even needed — a first pass suggests none are).

## Decisions

- **pytest + pytest-cov**, dev-only, split into `requirements-dev.txt` so
  the production Docker image doesn't install test tooling.
- **Coverage config lives in `pyproject.toml`** (`[tool.pytest.ini_options]`
  with `addopts = "--cov=app --cov-report=term-missing"`, and
  `[tool.coverage.report] fail_under = 100`) so a bare `pytest` enforces the
  bar locally, not just in CI.
- **Mock at the boundary, not the module**: patch `TwitterScraper._client`
  (the `twikit.Client` instance) and the `httpx.AsyncClient.post` call in
  `notifier.py`, rather than mocking `app.scraper`/`app.notifier` wholesale.
  This keeps the scraper/notifier's own logic (cookie caching, tweet
  parsing, missing-config short-circuit) genuinely exercised.
- **Patch call sites, not definitions**: modules that do
  `from app.scraper import scraper` (e.g. `tracker_service.py`, `main.py`)
  bind their own local name, so tests must patch e.g.
  `app.tracker_service.scraper` / `app.main.scraper`, not `app.scraper.scraper`.
- **Fresh `AsyncIOScheduler` per scheduler test**: `app/scheduler.py` keeps a
  module-level singleton. Tests monkeypatch that module attribute with a new
  `AsyncIOScheduler()` instance so tests don't share scheduler state or leak
  jobs into each other.
- **`.github/workflows/tests.yml`** runs `pip install -r requirements.txt -r
  requirements-dev.txt` then `pytest`, on push and pull_request.
- **Extend `.github/dependabot.yml`** with a `github-actions` ecosystem
  entry (weekly) now that a workflow file exists — this was explicitly
  flagged as a follow-up, not a goal, in the prior dependency-updates change.

## Risks / Trade-offs

- [Risk] `scheduler.py`'s `start_scheduler()` calls
  `asyncio.get_event_loop().call_later(5, ...)` to kick off an immediate
  first poll; in a test this timer is harmless because it only fires while
  its own event loop keeps running, and each test gets its own loop via
  pytest-asyncio → the timer never fires after the test function returns.
  Mitigation: don't assert on that side effect; only assert the interval job
  itself was registered (`_scheduler.get_job("poll_all_accounts")`).
- [Risk] 100% is a hard gate — a single untested line breaks CI for
  unrelated changes. Mitigation: this is intentional per the proposal
  ("asegurada" = enforced, not aspirational); keeping `app/` small keeps the
  bar cheap to maintain.
- [Risk] Dependabot bumping `twikit`/`fastapi`/etc. could change internal
  behavior the mocks assume. Mitigation: mocks target public, documented
  methods (`login`, `get_user_by_screen_name`, `get_user_tweets`,
  `load_cookies`, `save_cookies`) which are twikit's stable public API.
