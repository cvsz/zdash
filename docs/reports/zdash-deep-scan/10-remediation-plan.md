# zDash Remediation Plan

## P0 — Block final release

- [x] Run and capture full validation.
- [x] Production fail-closed validator tests — 14 tests in `test_production_safety.py`
- [x] High-risk action policy gate tests — 23 tests in `test_high_risk_action_policy.py`
- [x] Secret scan over tracked files — PASSED (safety-scan)
- [x] Frontend route smoke tests — 84 tests cover key pages
- [x] Provider fail-safe contract tests — 41 tests in `test_provider_contract_skeletons.py`

## P1 — Required before production prep

- [x] Add phase traceability matrix — `docs/reports/PHASE_TRACEABILITY_MATRIX.md`
- [x] Add release readiness report — `docs/releases/PHASE37_RELEASE_READINESS.md`
- [x] Add rollback runbook — `docs/runbooks/ROLLBACK_RUNBOOK.md`
- [x] Docker config validation in CI — docker compose config passes
- [x] Frontend safety-state tests — existing tests validate dashboard
- [x] Backend audit-event tests — enterprise tests cover audit

## P2 — Enterprise hardening

- [ ] Add SBOM generation
- [ ] Add SLO definitions
- [ ] Add incident response runbook
- [ ] Add backup/restore proof
- [ ] Add dependency update policy
- [ ] Add signed release attestation
