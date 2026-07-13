## ADDED Requirements

### Requirement: Automated dependency update pull requests
The project SHALL use Dependabot to automatically check for and propose
updates to pinned dependencies toward their latest available compatible
versions.

#### Scenario: Newer compatible version is published
- **WHEN** a newer version of a dependency pinned in `requirements.txt` is published
- **THEN** Dependabot opens a pull request updating that pin to the newer version, on its configured schedule

#### Scenario: No newer version available
- **WHEN** all pinned dependencies are already at their latest available version
- **THEN** Dependabot opens no pull request for that ecosystem on that run

### Requirement: Bounded and reviewable update volume
The project SHALL limit how many open Dependabot pull requests can exist at once, and updates SHALL always go through normal pull-request review before merging.

#### Scenario: Update PR limit reached
- **WHEN** the number of open Dependabot pull requests for an ecosystem reaches the configured limit
- **THEN** Dependabot does not open additional pull requests for that ecosystem until existing ones are merged or closed

#### Scenario: Dependabot PR opened
- **WHEN** Dependabot opens a dependency update pull request
- **THEN** the change is not merged automatically and requires the same review as any other pull request
