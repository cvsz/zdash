# Go-Live Rehearsal

## Purpose

Run a safe, repeatable go-live rehearsal that exercises every verification layer — runtime, health, safety locks, rollback readiness, and observability — and captures evidence for audit without enabling live trading or real external mutations.

## Safety

- All checks are read-only.
- No real broker, social, or IoT actions are triggered.
- No secrets are printed at any step.
- Evidence files contain **only** status values and redacted configuration keys.
- If production runtime is absent, all commands fail safely.

## Prerequisites

- Production runtime installed at `/opt/zdash/runtime`.
- `make validate-fast` passes.
- All Phase 39 verification scripts exist and are executable.
- Evidence directory `.runtime/evidence/` or `docs/reports/generated/` is writable.

## Commands

### Full Rehearsal (all phases)

```bash
make go-live-rehearsal
```

Runs in sequence:
1. Production runtime verification
2. Health verification
3. Safety locks verification
4. Rollback readiness verification
5. Observability verification
6. Evidence capture

### Individual Phase Commands

```bash
# Verify safety locks only
make go-live-safety-locks

# Capture evidence (must be run after other checks)
make go-live-evidence
```

### Direct Script Execution

```bash
# Full rehearsal
bash scripts/prod/run-go-live-rehearsal.sh

# Safety locks only
bash scripts/prod/verify-go-live-safety-locks.sh

# Evidence capture (saves to docs/reports/generated/)
bash scripts/prod/capture-go-live-evidence.sh

# Evidence capture to specific directory
ZDASH_EVIDENCE_DIR=.runtime/evidence bash scripts/prod/capture-go-live-evidence.sh
```

## Rehearsal Phases

| Phase | Script | What It Verifies |
|-------|--------|------------------|
| 1 — Runtime | `verify-prod-runtime.sh` | Runtime dir, systemd service, compose file, helpers |
| 2 — Health | `verify-prod-health.sh` | Backend health, safety check, frontend, ports |
| 3 — Safety Locks | `verify-go-live-safety-locks.sh` | DRY_RUN, LIVE_TRADING_ACK, MT5, risk guardian |
| 4 — Rollback | `verify-prod-rollback-readiness.sh` | Rollback docs, release GO, env safety values |
| 5 — Observability | `verify-prod-observability.sh` | Realtime endpoints, runbooks, compose config |
| 6 — Evidence | `capture-go-live-evidence.sh` | Captures all status, health, locks to evidence file |

## Interpreting Results

- **All phases pass**: System is rehearsal-ready. Proceed to `docs/runbooks/GO_LIVE_CHECKLIST.md`.
- **Any phase fails**: Investigate and resolve before proceeding.
  - Runtime failures → verify installation.
  - Health failures → check services.
  - Safety lock failures → review `.env.production`.
  - Rollback/observability failures → verify documentation exists.

## Evidence Files

Generated evidence files are written to:

- `docs/reports/generated/go-live-evidence-YYYYMMDD-HHMMSS.md` (default)
- `.runtime/evidence/go-live-evidence-YYYYMMDD-HHMMSS.md` (when `ZDASH_EVIDENCE_DIR=.runtime/evidence`)

These files are **not committed** by default (`.runtime/` is gitignored; `docs/reports/generated/` should be added to `.gitignore`).

## Failure Handling

| Failure | Action |
|---------|--------|
| Runtime not found | `sudo ./install-zdash-prod.sh` |
| Service unhealthy | `make prod-logs` to diagnose |
| Safety lock misconfigured | Fix `.env.production` values |
| Evidence capture fails | Check directory permissions |
| Rehearsal script fails mid-run | Fix the failing phase, re-run |

## Related Documents

- `docs/runbooks/GO_LIVE_CHECKLIST.md` — final go-live procedure
- `docs/runbooks/ROLLBACK_RUNBOOK.md` — rollback procedure
- `docs/runbooks/PRODUCTION_DRY_RUN_VERIFICATION.md` — dry-run verification reference
- `docs/releases/PHASE37_RELEASE_READINESS.md` — release readiness status
