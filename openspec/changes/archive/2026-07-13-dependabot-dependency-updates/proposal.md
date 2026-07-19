## Why

`requirements.txt` pins exact versions that only get bumped by hand — that's
already how a security push (fastapi/jinja2/python-multipart) got caught
late, after GitHub flagged 12 Dependabot alerts on push. There's currently no
automation that keeps dependencies current, so vulnerable or outdated pins
can sit unnoticed until the next manual review.

## What Changes

- Add a new capability, `dependency-updates`, requiring that project
  dependencies are kept up to date with their latest available versions via
  Dependabot's automated update pull requests.
- Add `.github/dependabot.yml` configuring Dependabot version updates for the
  `pip` ecosystem (`requirements.txt`) on a weekly schedule. No `github-actions`
  ecosystem entry yet — there are no workflow files in this repo to update.
- Document the Dependabot workflow (how PRs show up, how to review/merge them)
  in the README.

## Capabilities

### New Capabilities
- `dependency-updates`: Dependabot opens automated pull requests to update
  pinned dependencies to their latest available compatible versions, and
  security-relevant updates are prioritized.

### Modified Capabilities
- (none — this doesn't change any existing application behavior)

## Impact

- Affected files: `.github/dependabot.yml` (new), `README.md` (new section).
- No runtime code changes; this is repo/CI configuration only.
- Once merged, Dependabot will start opening PRs against the repo's default
  branch on its configured schedule — those PRs still need human review
  before merging, same as any other PR.
