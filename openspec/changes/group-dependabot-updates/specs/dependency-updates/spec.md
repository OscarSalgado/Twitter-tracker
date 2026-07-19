## ADDED Requirements

### Requirement: Grouped minor and patch updates
The project SHALL configure Dependabot to bundle same-run minor and patch version updates within an ecosystem into a single pull request, while major version updates SHALL remain ungrouped.

#### Scenario: Multiple minor/patch updates available in one run
- **WHEN** more than one dependency in the same ecosystem has an available minor or patch update in the same Dependabot run
- **THEN** Dependabot opens a single pull request containing all of those minor/patch updates for that ecosystem

#### Scenario: Major version update available
- **WHEN** a dependency has an available major version update
- **THEN** Dependabot opens a separate, individual pull request for that update, not bundled with minor/patch changes
