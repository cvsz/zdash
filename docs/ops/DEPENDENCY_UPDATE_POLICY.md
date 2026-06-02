# Dependency Update Policy

## Cadence

| Activity | Frequency | Responsible |
|----------|-----------|-------------|
| Dependency review | Weekly (Monday) | Dependabot / automated PR review |
| Non-security updates | Monthly (first week) | Engineering team |
| Security patches (CVSS >= 4) | Within 7 days | On-call engineer |
| Security patches (CVSS >= 7) | Within 48 hours | On-call engineer |
| Critical security patches (CVSS >= 9) | Within 24 hours | Security team + engineering |

## Review Flow

### Automated Dependency PRs
1. Dependabot or automated tool creates a PR with dependency update
2. PR includes changelog/release notes for the updated package
3. PR title prefix: `deps:` for non-security, `security:` for security patches

### Review Requirements
- **Non-security updates**: Review by 1 engineer, merge after CI passes
- **Security patches (CVSS 4–6)**: Review by 1 engineer + security team notification
- **Security patches (CVSS >= 7)**: Review by 2 engineers, merge after CI passes and security team acknowledgment

### Review Checklist
- [ ] Changelog reviewed for breaking changes
- [ ] Test suite passes (backend + frontend)
- [ ] Build succeeds
- [ ] No new vulnerabilities introduced (verified by safety scan)
- [ ] Lockfile updated (not just manifest)
- [ ] No unintended dependency drift

## Lockfile Update Rules

- Both `package-lock.json` (frontend) and lock files (pip) must be committed with dependency changes
- Lockfiles must not be manually edited — regenerate via `npm install` or `pip install`
- Lockfile-only PRs (no manifest changes) are acceptable for security patches
- Renovate/Dependabot config should target weekly schedule for non-security updates

## Backend Dependencies

Managed via `backend/pyproject.toml` and `backend/requirements.txt`.

```bash
cd backend
source .venv/bin/activate
pip list --outdated
pip install --upgrade <package>
pip freeze > requirements.txt
```

Validation:
```bash
python -m ruff check app tests
python -B -m pytest -q
```

## Frontend Dependencies

Managed via `frontend/package.json`.

```bash
cd frontend
npx npm-check-updates
npm install --legacy-peer-deps --no-audit --fund=false
```

Validation:
```bash
npm test
npm run build
```

## CI Gates

All dependency update PRs must pass:
1. `make safety-scan` — no new forbidden patterns
2. `make backend-check` — ruff + pytest
3. `make frontend-check` — vitest + build
4. Secret scan — no secrets exposed
5. License scan — no incompatible license introductions

## Dependency Freeze

Before a release:
1. All dependencies are pinned to specific versions
2. Lockfiles are committed and reviewed
3. A full validation run (`make validate`) passes
4. Any CVSS >= 7 vulnerabilities must be resolved or documented

## Rollback Plan

If a dependency update causes issues:

1. **Immediate (within 1 hour)**: Revert the dependency PR, deploy the previous lockfile
2. **Short-term (within 24 hours)**: Pin the problematic dependency to the previous working version
3. **Long-term (next release)**: Investigate root cause, add regression test, re-attempt update

```bash
# Quick rollback of a frontend dependency
cd frontend
npm install <package>@<previous-version> --legacy-peer-deps
npm test
npm run build
```

```bash
# Quick rollback of a backend dependency
cd backend
source .venv/bin/activate
pip install <package>==<previous-version>
python -B -m pytest -q
pip freeze > requirements.txt
```

## Exceptions

- Development-only dependencies (e.g., test runners, linters) may be updated more aggressively
- Transitive dependencies without breaking changes may be auto-merged if CI passes
- Any exception to this policy requires written approval from the engineering lead
