# Phase 40 — Production Install Rehearsal + Go-Live Evidence Capture Report

Generated: Phase 40 implementation
Scope: Go-live rehearsal workflow with evidence capture

## Summary

Implemented a safe, repeatable go-live rehearsal workflow that exercises all verification layers across Phases 39 and 40, and captures auditable evidence of runtime state, health, safety locks, and documentation readiness — without enabling live trading or real external mutations.

## Deliverables

| Artifact | Description |
|----------|-------------|
| `scripts/prod/verify-go-live-safety-locks.sh` | Verifies 5 safety env values are locked (DRY_RUN, LIVE_TRADING_ACK, MT5_ENABLED, PRODUCTION_ALLOW_LIVE_ACTIONS, RISK_GUARDIAN_ENABLED) plus service status |
| `scripts/prod/capture-go-live-evidence.sh` | Captures service status, health, safety locks, and doc verification into timestamped evidence file |
| `scripts/prod/run-go-live-rehearsal.sh` | Orchestrates all 6 phases: runtime → health → safety locks → rollback → observability → evidence |
| `docs/runbooks/GO_LIVE_REHEARSAL.md` | Runbook with commands, phase descriptions, and failure handling |
| `docs/reports/PHASE40_GO_LIVE_REHEARSAL_REPORT.md` | This report |

## Makefile Targets Added

| Target | Description |
|--------|-------------|
| `go-live-rehearsal` | Run full go-live rehearsal (all 6 phases) |
| `go-live-evidence` | Capture go-live evidence only |
| `go-live-safety-locks` | Verify go-live safety locks only |
| `phase40-validate` | Validate Phase 40 deliverables |

## Verification Results

### Safety

- [x] `DRY_RUN=true` verified as runtime invariant
- [x] `LIVE_TRADING_ACK=false` verified
- [x] `MT5_ENABLED=false` verified
- [x] `PRODUCTION_ALLOW_LIVE_ACTIONS=false` verified
- [x] `RISK_GUARDIAN_ENABLED=true` verified
- [x] No secrets printed — only key names and status values
- [x] Evidence files contain redacted config (key names only, no values)
- [x] All scripts fail safely when production runtime absent

### Evidence Capture

- [x] Captures `systemctl status zdash`
- [x] Captures `docker compose ps`
- [x] Captures backend health and safety check responses
- [x] Captures frontend HTTP status code
- [x] Captures safety lock values (key names only)
- [x] Captures documentation verification (6 docs checked)
- [x] Evidence written to timestamped file: `docs/reports/generated/go-live-evidence-*.md`

### Runtime Absent Behavior

- [x] `verify-go-live-safety-locks.sh` — "Production runtime not found"
- [x] `capture-go-live-evidence.sh` — "Production runtime not found"
- [x] `run-go-live-rehearsal.sh` — "Production runtime not found"
- [x] `make go-live-rehearsal` — fails at first phase with clear message
- [x] `make go-live-safety-locks` — fails safely

### Validation

- [x] `make validate-fast` passes
- [x] `make phase39-validate` passes
- [x] `make phase40-validate` passes
- [x] No duplicate Makefile targets
- [x] No .env files tracked by git
- [x] Release GO remains documented

## Safety Notes

- All scripts are read-only; no mutations are performed.
- Evidence files contain only status codes and configuration key names — no secrets.
- The rehearsal can be run any number of times without side effects.
- Evidence is written to `docs/reports/generated/` by default, which is gitignored.
- The go-live rehearsal is a prerequisite step in the `docs/runbooks/GO_LIVE_CHECKLIST.md`.
