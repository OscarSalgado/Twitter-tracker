## Context

`requirements.txt` currently has hand-pinned versions. GitHub already runs
Dependabot *security alerts* on this repo (it flagged 12 vulnerabilities on
an earlier push), but there is no `dependabot.yml`, so there are no routine
*version update* PRs — only ad-hoc manual bumps.

## Goals / Non-Goals

**Goals:**
- Get Dependabot opening PRs on a regular cadence to bump `requirements.txt`
  pins toward their latest compatible versions.
- Keep the config minimal — one ecosystem, one directory, weekly cadence.

**Non-Goals:**
- Auto-merging Dependabot PRs. They still go through normal review.
- Adding a `github-actions` ecosystem entry — there are no workflow files in
  this repo yet, so there's nothing for Dependabot to update there. Add it
  later if/when CI workflows are introduced.
- Changing the pinning strategy (exact `==` pins stay; Dependabot bumps the
  pinned value directly, which is the standard `pip` ecosystem behavior).

## Decisions

- **Weekly schedule** over daily: this is a low-traffic solo project: daily
  PRs would be noise, weekly is enough to stay current without review fatigue.
- **`pip` ecosystem pointed at `/`**: Dependabot's `pip` ecosystem reads
  `requirements.txt` at the given directory; the repo keeps it at the root,
  so `directory: "/"` is correct and needs no further path config.
- **`open-pull-requests-limit: 5`**: caps how many update PRs can be open at
  once so a burst of upstream releases doesn't flood the PR list.

## Risks / Trade-offs

- [Risk] A Dependabot PR bumps a dependency to a version with a breaking
  change → Mitigation: PRs are reviewed and go through the same manual
  smoke test (`uvicorn` boot + `/healthz`) as any other dependency change
  before merging; nothing auto-merges.
- [Risk] Dependabot needs to be enabled for the repository/org in GitHub
  settings for the config to take effect → Mitigation: called out in the
  README as a one-time check if PRs don't start appearing.
