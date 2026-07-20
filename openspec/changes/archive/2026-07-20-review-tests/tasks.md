## 1. Fix failing tests

- [x] 1.1 Read the current `/healthz` implementation in `app/main.py` and update `tests/test_main.py::test_healthz_is_unauthenticated` to assert the actual response shape, including the `twitter_login` field.
- [x] 1.2 Read the current `poll_all_accounts` implementation in `app/tracker_service.py` and update `tests/test_tracker_service.py::test_poll_all_accounts_aggregates_across_accounts` to mock `scraper.login()` (or the relevant login-check call) so the test exercises the intended aggregation path.
- [x] 1.3 Run `pytest -q` and confirm both previously-failing tests now pass.

## 2. Close coverage gaps

- [x] 2.1 Add a test in `tests/test_scraper.py` exercising the login-failure branch at `app/scraper.py:39`.
- [x] 2.2 Add a test in `tests/test_tracker_service.py` exercising the login-retry-failed / skip-this-poll branch at `app/tracker_service.py:93-102`.
- [x] 2.3 Run `pytest --cov=app --cov-report=term-missing` and confirm `app/` reaches 100% line coverage.

## 3. Review assertion strength

- [x] 3.1 Skim the tests touched in tasks 1 and 2, plus any tests directly adjacent to them, for assertions that only check status codes or truthiness where a body/side-effect/state assertion would catch more regressions; strengthen any found.
- [x] 3.2 Confirm no test was weakened or made to assert on incidental/mocked behavior instead of real app behavior.

## 4. Verify

- [x] 4.1 Run `pytest -q` (full suite) and confirm all tests pass with 100% coverage and the coverage gate satisfied.
- [x] 4.2 Confirm no file under `app/` was modified as part of this change (test-only diff).
