## Context

Running `pytest` on the current tree shows 2 failing tests and 96.54% coverage (gate requires 100%):

- `tests/test_main.py::test_healthz_is_unauthenticated` asserts `/healthz` returns `{"status": "ok"}`, but the endpoint (`app/main.py`) now also returns a `twitter_login` field.
- `tests/test_tracker_service.py::test_poll_all_accounts_aggregates_across_accounts` mocks `app.tracker_service.poll_account` but not `scraper.login()`. `poll_all_accounts` (`app/tracker_service.py`) now calls `scraper.login()` first and skips the poll entirely if login fails, so the un-mocked login raises `RuntimeError` (missing credentials), is caught, and the function returns 0 instead of aggregating.
- Coverage gaps: `app/scraper.py` line 39 (the login-failure branch) and `app/tracker_service.py` lines 93-102 (the login-retry-failed / skip-this-poll branch) have no test exercising them.

## Goals / Non-Goals

**Goals:**
- Bring the suite back to green against current `app/` behavior.
- Reach 100% line coverage by adding tests for the two known gaps.
- Spot-check other tests for weak assertions (status-code-only checks where a body/side-effect assertion would catch more) and strengthen any found.

**Non-Goals:**
- No changes to `app/` behavior, endpoints, or scheduling logic.
- No new test infrastructure, fixtures libraries, or CI workflow changes.
- Not a full rewrite of the suite — targeted fixes plus a lightweight review pass.

## Decisions

- **Fix tests to match current app behavior, not the reverse.** The app's `/healthz` and `poll_all_accounts` changes appear intentional (health check now reports Twitter login status; polling now skips accounts when login fails rather than crashing). Since the proposal is test-only, tests are updated to assert the current, presumably-correct behavior.
- **Mock `scraper.login()` via the same `patch`/`AsyncMock` pattern already used for `poll_account`** in `test_tracker_service.py`, keeping consistency with existing test style rather than introducing a new mocking helper.
- **Add coverage tests as new, narrowly-scoped test functions** (e.g., `test_login_failure_raises` in `test_scraper.py`, `test_poll_all_accounts_skips_when_login_fails` in `test_tracker_service.py`) rather than expanding existing tests, so each test keeps a single clear intent.
- **Weak-assertion review is opportunistic, not exhaustive**: fix what's found while touching these files rather than auditing all 8 test files line by line, since the proposal scope is the coverage/failure gap, not a full test-quality audit.

## Risks / Trade-offs

- [Risk: the actual intended behavior of `/healthz` or `poll_all_accounts` is ambiguous from code alone] → Mitigation: read the current implementation directly (`app/main.py`, `app/tracker_service.py`, `app/scraper.py`) before writing assertions, and assert on the literal current return values/control flow rather than guessing.
- [Risk: fixing tests to match current behavior could paper over an actual bug in `app/`] → Mitigation: this proposal is test-only by design; if a review during implementation reveals an actual app bug, flag it separately rather than silently asserting on broken behavior.

## Migration Plan

Not applicable — no deployment or rollback; this is a test-only change merged like any other commit once green.
