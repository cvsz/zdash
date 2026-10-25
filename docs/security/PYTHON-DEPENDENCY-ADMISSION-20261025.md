# Python Dependency Audit Remediation — 2026-10-25

## Finding

The exact-head `security-ci` run for `dependabot/npm_and_yarn/frontend/vite-8.3.5` (#92) failed its `pip-audit -r backend/requirements.lock` step on 2026-10-21. The locked graph contained 14 advisories for `PyJWT==2.13.0` and one advisory for `certifi==2026.7.22` (15 findings across two packages).

## Change

- Pin `PyJWT==2.15.1`, above the audit's reported fixed versions (2.14.0/2.15.0).
- Pin `certifi==2026.10.23`, above the reported fixed version `2026.10.19`.
- Keep the existing `pip-audit` gate blocking; do not suppress advisories or weaken the workflow.

## Verification required

Run `pip-audit -r backend/requirements.lock`, the full Python test suite, dependency review, CodeQL, and exact-head CI. Verify that the lockfile remains installable and that auth/JWT regression tests still pass.

## Rollback

Do not roll back to the known-vulnerable package versions. If a compatibility regression appears, select a different upstream-fixed version and rerun the full audit and test suite.

No production deployment or financial operation is part of this change.
