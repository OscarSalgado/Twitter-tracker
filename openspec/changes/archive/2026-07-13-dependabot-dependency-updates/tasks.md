## 1. Dependabot configuration

- [x] 1.1 Create `.github/dependabot.yml` with a `pip` ecosystem entry for
      `requirements.txt` at the repo root, weekly schedule, and
      `open-pull-requests-limit: 5`
- [x] 1.2 Validate the YAML is well-formed (`python3 -c "import yaml,
      sys; yaml.safe_load(open('.github/dependabot.yml'))"`)

## 2. Documentation

- [x] 2.1 Add a short "Actualización de dependencias" section to `README.md`
      explaining that Dependabot opens weekly PRs against `requirements.txt`
      and that they still require manual review/merge

## 3. Verification

- [x] 3.1 Confirm the app still boots after this change (no runtime code
      touched, but re-run the existing smoke test: `uvicorn app.main:app`
      then `curl /healthz` and `curl -u admin:<pass> /`)
- [x] 3.2 Run `openspec validate --changes --strict` for this change

## 4. Finalize

- [x] 4.1 Archive the change (`openspec archive dependabot-dependency-updates`)
      to merge the `dependency-updates` delta spec into `openspec/specs/`
