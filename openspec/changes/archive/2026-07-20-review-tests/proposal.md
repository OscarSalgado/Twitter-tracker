## Why

The test suite is currently red on `main`'s working tree and under-covered: two tests fail because they were not updated when `app/main.py`'s `/healthz` endpoint and `app/tracker_service.py`'s `poll_all_accounts` login-retry logic changed, and coverage of `app/` sits at 96.54% (below the 100% gate defined in `test-coverage`), with gaps in `app/scraper.py` (login-failure branch) and `app/tracker_service.py` (login-retry/skip-on-failure branch). This blocks merges and CI on the `tests.yml` workflow and undermines confidence in the coverage gate as a real regression signal. This needs fixing now because every subsequent change to tracker polling or health checks is currently landing against a suite that cannot validate it.

## What Changes

- Fix `tests/test_main.py::test_healthz_is_unauthenticated` to assert on the current `/healthz` response shape, which now includes a `twitter_login` field alongside `status`.
- Fix `tests/test_tracker_service.py::test_poll_all_accounts_aggregates_across_accounts` to mock `scraper.login()` (or the login-check path `poll_all_accounts` now calls before polling), matching the login-retry-and-skip behavior added to `tracker_service.py`.
- Add test coverage for the previously-uncovered branches: the login-failure path in `app/scraper.py` (line 39) and the login-retry-failed / skip-this-poll path in `app/tracker_service.py` (lines 93-102), restoring 100% line coverage.
- Review existing tests for assertions that are too weak to catch regressions (e.g., only checking status codes, not response bodies or side effects) and strengthen the weakest ones found during this pass.
- No changes to application behavior — this is test-only; any discrepancy between a test's expectation and the app's actual current behavior is resolved by fixing the test to match intended behavior, not by changing `app/`.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
- `test-coverage`: no requirement text changes, but this change is what brings the existing "100% line coverage" and "tests never touch real external services" requirements back into compliance after drift.

## Impact

- Affected files: `tests/test_main.py`, `tests/test_tracker_service.py`, `tests/test_scraper.py`, and potentially other test files if weak assertions are found during review.
- No changes to `app/` source, dependencies, or the CI workflow itself.
- No risk to X's Terms of Service or rate limits: this change only touches mocked, offline tests and adds no new network calls.
