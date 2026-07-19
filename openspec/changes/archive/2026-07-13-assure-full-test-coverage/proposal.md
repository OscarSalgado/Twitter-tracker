## Why

There is currently no automated test suite. Every behavior spec added so far
(account tracking, tweet polling, notifications, the dashboard) is only
verified by hand with `uvicorn` + `curl`. That doesn't scale and doesn't run
on every change, so regressions can land silently — including in the
Dependabot update PRs the project now relies on to bump dependencies.

## What Changes

- Add a new capability, `test-coverage`, requiring that the codebase carries
  an automated test suite with 100% line coverage of `app/`, enforced in CI
  so a coverage regression fails the build rather than just being noticed.
- Add `pytest` + `pytest-cov` (dev-only dependency, split into
  `requirements-dev.txt`) and a full test suite under `tests/` covering
  every module in `app/` (config, database, models, scraper, notifier,
  tracker_service, scheduler, main), using mocks for the external Twitter
  and Telegram calls — no real network access or credentials in tests.
- Add a GitHub Actions workflow (`.github/workflows/tests.yml`) that runs
  the suite with `--cov-fail-under=100` on every push/PR.
- Extend `.github/dependabot.yml` with a `github-actions` ecosystem entry,
  since this change introduces the repo's first workflow file (follow-up
  already flagged as a non-goal in the earlier dependency-updates design).

## Capabilities

### New Capabilities
- `test-coverage`: the project SHALL maintain an automated test suite with
  100% line coverage of the application code, enforced in CI.

### Modified Capabilities
- (none — this doesn't change any existing application behavior, only adds
  verification for it)

## Impact

- Affected files: `requirements-dev.txt` (new), `tests/**` (new),
  `pytest.ini` or `pyproject.toml` (new, coverage config),
  `.github/workflows/tests.yml` (new), `.github/dependabot.yml` (modified
  to add the `github-actions` ecosystem), `README.md` (new section).
- No changes to `app/` runtime behavior are expected; if achieving 100%
  coverage requires small refactors (e.g. splitting an unreachable branch),
  those are implementation details, not spec changes.
