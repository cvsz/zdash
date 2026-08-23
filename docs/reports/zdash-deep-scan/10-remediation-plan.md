# zDash Remediation Plan

Status refreshed 2026-08-23 against commit f34c874 (v0.42.0-rc3 line).

## P0

- [x] Run and capture full validation. — see 09-validation-log.md (2026-08-23)
- [x] Add production fail-closed validator tests. — covered by backend suite (auth/RBAC/tenant isolation fail-closed tests)
- [x] Add high-risk action policy gate tests. — see docs/reports/high-risk-route-policy-matrix.md and RBAC route tests
- [x] Add secret scan over tracked files and release artifacts. — security-ci secret pattern scan + dependency-review + pip-audit/npm audit (blocking as of f34c874)

## P1

- [x] Add phase traceability matrix. — docs/reports/PHASE_TRACEABILITY_MATRIX.md
- [x] Add provider adapter contract tests. — app/tests/test_provider_contract_skeletons.py
- [~] Add frontend safety-state tests. — partial; dry-run/approval states asserted in App/route tests, expand coverage for mutation buttons
- [x] Add backend audit-event tests. — event bus / observability request logging tested in backend suite

## P2

- [x] Add SBOM. — release-evidence workflow (CycloneDX, green on v0.42.0-rc3)
- [ ] Add SLO/runbooks.
- [ ] Add incident response docs.
- [x] Add backup/restore proof. — PG 18.6 local rehearsal recorded 2026-08-23 in docs/operations/postgresql-major-upgrade-plan.md; production-equivalent restore still outstanding
