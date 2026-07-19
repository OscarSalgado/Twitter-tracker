## Why

Dependabot currently opens a separate pull request for every individual dependency bump across the `pip` and `github-actions` ecosystems. Most of these are low-risk minor/patch updates, so the project accumulates review overhead from many small PRs instead of a few consolidated ones.

## What Changes

- Add `groups:` configuration to `.github/dependabot.yml` for both the `pip` and `github-actions` ecosystems, bundling `minor` and `patch` updates into a single grouped pull request per ecosystem per run.
- Leave `major` version updates ungrouped so they continue to open their own individual pull request and get closer review.
- No change to schedule (`weekly`) or `open-pull-requests-limit` (`5`).

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
- `dependency-updates`: add a requirement that minor/patch updates within an ecosystem are grouped into a single pull request, while major updates remain individually reviewable.

## Impact

- `.github/dependabot.yml`: add `groups` blocks to both ecosystem entries.
- `openspec/specs/dependency-updates/spec.md`: new requirement + scenarios for grouped updates.
- No application code, X API usage, or rate-limit behavior is affected — this is CI/dependency-tooling configuration only.
