# Test Coverage Specification

## Purpose
Makes sure every behavior spec in this project (account tracking, tweet polling, notifications, the dashboard) stays verified by an automated, enforced test suite instead of by hand, so regressions — including ones introduced by Dependabot's own dependency-update PRs — get caught before merge rather than in production.

## Requirements

### Requirement: 100% line coverage of application code
The project SHALL maintain an automated test suite that exercises 100% of the lines in `app/`, measured by `pytest-cov`, and every test in that suite SHALL pass against the current behavior of `app/`.

#### Scenario: Full suite run
- **WHEN** the test suite is run with coverage measurement against `app/`
- **THEN** every line in `app/` is reported as covered and every test passes

#### Scenario: Uncovered line introduced
- **WHEN** a code change adds a line in `app/` that no test exercises
- **THEN** the coverage report shows less than 100% for that run

#### Scenario: Test drifts from app behavior
- **WHEN** application behavior changes (e.g., a response shape or a control-flow branch) without the corresponding test being updated
- **THEN** the affected test fails, and the failure is treated as a defect in the test suite to be fixed rather than ignored or skipped

### Requirement: Coverage gate is enforced, not advisory
The project SHALL fail the test run itself when line coverage of `app/` drops below 100%, both locally and in CI.

#### Scenario: Coverage drops below 100%
- **WHEN** `pytest` is run and measured coverage of `app/` is below 100%
- **THEN** the test run exits with a non-zero status, independent of whether individual tests passed

#### Scenario: CI runs the suite
- **WHEN** a commit is pushed or a pull request is opened
- **THEN** a CI workflow installs dependencies and runs the full test suite with the coverage gate

### Requirement: Tests never touch real external services
The project's tests SHALL run without any real network calls to Twitter/X or Telegram, and without requiring real credentials.

#### Scenario: Suite run with no credentials configured
- **WHEN** the test suite is run in an environment with no Twitter or Telegram credentials set
- **THEN** all tests pass, because every Twitter/X and Telegram call is mocked at the boundary

