# PyJWT Security Update — zDash (v338)

## Scope and evidence

- Base commit: `0627071ea508c32694a82d38e1a977a8a323eefe` (`main`).
- Security CI failure: `https://github.com/cvsz/zdash/actions/runs/39122908241` (2026-10-18 UTC), job `117661984678`.
- `pip-audit -r backend/requirements.lock` identified 14 advisories for PyJWT 2.13.0; 2 advisories require at least 2.15.0.
- PyJWT 2.15.1 published 2026-09-28 with PyPI provenance and SHA-256 wheel `42d59d631f7768a1028a64c7ff581a9bf7519804daf91fc5b6c56e30eec5e193`.

## Change

Set both runtime and development lock files to `PyJWT==2.15.1`; raise the lower bound in `backend/requirements.txt` and `backend/pyproject.toml` to `PyJWT>=2.15.1`. All other dependency versions remain unchanged.

## Required validation before merge

```bash
python3 -m pip install -r backend/requirements-dev.lock
python3 -m unittest discover -s tests -p 'test_pyjwt_dependency_boundary_v338.py' -v
make backend-lint
make backend-test
python3 -m pip install pip-audit
python3 -m pip_audit -r backend/requirements.lock
make validate-fast
```

Ensure a fresh Python environment for resolver/install tests; do not install into production or use real credentials. Review JWT algorithm allow-lists (never mix HS* and RS*/ES* for a single verifier). Verify external OIDC/JWKS integrations separately. Pin any wheel used in an offline promotion to its official PyPI checksum.

## Rollback

Revert the focused commit on its feature branch, or use `git apply -R` with the attached patch before commit. **Do not deploy the vulnerable PyJWT 2.13.0** as a security rollback. If the new release breaks compatibility, halt deployment, keep the service behind a safe admission gate, and prepare a supported patched version with passing security checks.

## Admission

Local dependency-contract tests do not establish hosted CI success or production readiness. Require an exact-head passing security CI, independent review, and staging auth regression before merge/deployment.
