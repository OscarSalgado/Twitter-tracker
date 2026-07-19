## 1. Update Dependabot configuration

- [x] 1.1 Add a `groups` block to the `pip` entry in `.github/dependabot.yml` grouping `minor` and `patch` update types into a single group (e.g. `minor-patch`)
- [x] 1.2 Add the same `groups` block shape to the `github-actions` entry in `.github/dependabot.yml`
- [x] 1.3 Confirm `major` updates are left outside the group definitions so they remain individually opened

## 2. Update specs

- [x] 2.1 Sync the `dependency-updates` delta spec (grouped minor/patch requirement) into `openspec/specs/dependency-updates/spec.md`

## 3. Verify

- [x] 3.1 Validate YAML syntax of `.github/dependabot.yml` (e.g. `python -c "import yaml; yaml.safe_load(open('.github/dependabot.yml'))"`)
- [x] 3.2 Run `openspec validate group-dependabot-updates --strict` (or equivalent) to confirm the change's artifacts are well-formed
- [ ] 3.3 Manually inspect the GitHub repo's Dependabot "Insights" page after the next scheduled run (or trigger via "Check for updates" in the UI) to confirm updates are grouped as expected
