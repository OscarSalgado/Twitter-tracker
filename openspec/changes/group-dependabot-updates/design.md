## Context

`.github/dependabot.yml` currently has two `updates` entries (`pip`, `github-actions`), each weekly with `open-pull-requests-limit: 5` and no `groups` key. Dependabot therefore opens one PR per updatable dependency per run. This is a small, low-risk config-only change — no design doc would strictly be required, but it's included here to record the grouping strategy and the boundary between grouped and ungrouped updates.

## Goals / Non-Goals

**Goals:**
- Reduce Dependabot PR volume by bundling same-run minor/patch updates per ecosystem into one PR.
- Keep major version bumps ungrouped so they still get individual, closer review.

**Non-Goals:**
- Changing update schedule, PR limits, or adding new ecosystems.
- Auto-merging any Dependabot PRs (grouped or not) — review is still required per the existing `dependency-updates` spec.

## Decisions

- **Use Dependabot's native `groups` key** (no custom automation/bot). Each ecosystem entry gets one group, e.g.:
  ```yaml
  groups:
    minor-patch:
      update-types: ["minor", "patch"]
  ```
  Alternative considered: grouping by dependency name/pattern (e.g. all `fastapi`-related packages together) — rejected as unnecessary complexity for a small, flat dependency set.
- **Apply the same group shape to both `pip` and `github-actions`** for consistency, rather than only grouping one ecosystem.
- **Major updates stay ungrouped** (Dependabot's default behavior when a version isn't matched by any group) so breaking changes remain individually visible and reviewable.

## Risks / Trade-offs

- [Risk] A grouped PR bundling multiple package bumps could fail CI due to one bad dependency, blocking all bundled updates → Mitigation: normal PR review/CI already gates merges; a failing grouped PR can be split or the offending update excluded manually, same as today's failure mode for any single-dependency PR.
- [Risk] Grouping reduces per-dependency changelog visibility in the PR title → Mitigation: Dependabot lists all bundled dependency versions in the grouped PR body.
