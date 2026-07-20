## MODIFIED Requirements

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
