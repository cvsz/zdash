# Operator Handoff

## Purpose

This document provides the complete operator manual for running, monitoring, and recovering zDash in production. It covers all essential operations — start, stop, health, logs, backup, rollback, and emergency safety lock checks.

## Quick Reference

| Operation | Command |
|-----------|---------|
| Start stack | `make prod-up` |
| Stop stack | `make prod-down` |
| Service status | `make prod-status` |
| Health check | `make prod-health` |
| Backend logs | `make prod-backend-logs` |
| Backup | `make prod-backup` |
| Update/rebuild | `make prod-update` |
| Full rehearsal | `make go-live-rehearsal` |
| Safety locks | `make go-live-safety-locks` |
| Rollback | See `ROLLBACK_RUNBOOK.md` |

## System Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│   Database   │
│  :5173/:8080 │     │   :8005      │     │  PostgreSQL  │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                    ┌───────▼───────┐
                    │    Redis      │
                    └───────────────┘
```

## Start/Stop

### Start Production Stack

```bash
make prod-up
```

This starts all services via Docker Compose: postgres, redis, backend, frontend, nginx.

### Stop Production Stack

```bash
make prod-down
```

Stops all services gracefully (30-second timeout).

### Restart Production Stack

```bash
make prod-restart
```

Restarts the systemd service which manages the Docker Compose stack.

## Health Monitoring

### Health Check

```bash
make prod-health
```

Runs the production health helper which checks:
- Backend `/health` endpoint
- Backend `/api/admin/safety-check`
- Frontend HTTP status

### Service Status

```bash
make prod-status
```

Shows systemd service status for the `zdash` unit.

### Docker Compose Status

```bash
make prod-ps
```

Lists all running Docker Compose services.

## Logs

### Backend Logs

```bash
make prod-backend-logs
```

### Service-specific Logs

```bash
SERVICE=nginx make prod-logs
SERVICE=frontend make prod-logs
SERVICE=postgres make prod-logs
```

## Backup

### Run Backup

```bash
make prod-backup
```

Creates a timestamped backup archive including the database dump and configuration.

### Verify Backup

```bash
bash scripts/verify-backup.sh <backup-file>
```

## Update/Rebuild

### Update Production Stack

```bash
make prod-update
```

Pulls latest images, rebuilds if needed, and restarts services.

## Safety Locks

### Verify Safety Locks

```bash
make go-live-safety-locks
```

Verifies the following safety invariants are set in `.env.production`:

| Key | Expected | Purpose |
|-----|----------|---------|
| `DRY_RUN` | `true` | Prevents real broker execution |
| `LIVE_TRADING_ACK` | `false` | Blocks trade confirmation |
| `MT5_ENABLED` | `false` | Prevents MT5 connection |
| `PRODUCTION_ALLOW_LIVE_ACTIONS` | `false` | Blocks all live mutations |
| `RISK_GUARDIAN_ENABLED` | `true` | Enables risk check enforcement |

### Emergency Halt

```bash
curl -X POST http://localhost:8005/api/risk/emergency-halt
curl http://localhost:8005/api/risk/status
```

### Kill Switch

```bash
curl -X POST http://localhost:8005/api/risk/kill-switch-reset
```

See: `docs/runbooks/KILL_SWITCH.md`

## Go-Live Rehearsal

Before any production deployment, run the full go-live rehearsal:

```bash
make go-live-rehearsal
```

This runs 6 phases:
1. Runtime verification
2. Health verification
3. Safety locks verification
4. Rollback readiness
5. Observability verification
6. Evidence capture

See: `docs/runbooks/GO_LIVE_REHEARSAL.md`

## Release

### Create Release Candidate

```bash
make release-candidate
```

Verifies readiness, collects evidence, and generates release candidate notes.

### Collect Release Evidence

```bash
make release-evidence
```

Gathers validation results, makefile targets, script/doc inventory, and safety lock documentation.

### Verify Release Readiness

```bash
make release-readiness
```

Checks all phase 38-41 docs exist, release decision is GO, safety locks are documented, and no secrets are tracked.

### Publish Release

```bash
CONFIRM_RELEASE=yes make release-push
CONFIRM_RELEASE=yes make gh-release
```

## Rollback

In the event of a failed deployment:

1. **Halt** operations: `curl -X POST http://localhost:8005/api/risk/emergency-halt`
2. **Stop** services: `make prod-down`
3. **Revert** to previous image tag
4. **Restore** database if needed: `bash scripts/restore-db.sh <backup-file>`
5. **Restart**: `make prod-up`
6. **Verify**: Check health and safety endpoints

See: `docs/runbooks/ROLLBACK_RUNBOOK.md`

## Incident Response

1. **Halt** risky operations
2. **Diagnose** using logs: `make prod-logs`
3. **Recover** using rollback or fix-forward
4. **Document** in incident report

See: `docs/runbooks/INCIDENT_RESPONSE.md`

## Production Verification Scripts

All verification scripts are located in `scripts/prod/`:

| Script | Purpose |
|--------|---------|
| `verify-prod-runtime.sh` | Check runtime directory, systemd, compose, helpers |
| `verify-prod-health.sh` | Check health endpoints and port exposure |
| `verify-prod-rollback-readiness.sh` | Check safety env values and rollback docs |
| `verify-prod-observability.sh` | Check runbooks, compose config, realtime docs |
| `verify-go-live-safety-locks.sh` | Verify all 5 safety env values are locked |
| `capture-go-live-evidence.sh` | Capture runtime evidence to timestamped file |
| `run-go-live-rehearsal.sh` | Run all 6 phases of go-live rehearsal |

## Release Scripts

All release scripts are located in `scripts/release/`:

| Script | Purpose |
|--------|---------|
| `verify-release-readiness.sh` | Verify all phase docs, scripts, safety locks, no secrets |
| `collect-release-evidence.sh` | Collect validation results and inventory to evidence file |
| `create-release-candidate.sh` | Verify readiness, collect evidence, generate candidate notes |

## Emergency Contacts

For production incidents:
1. Check logs: `make prod-backend-logs`
2. Check status: `make prod-status`
3. Halt if needed: `curl -X POST http://localhost:8005/api/risk/emergency-halt`
4. Rollback: Follow `docs/runbooks/ROLLBACK_RUNBOOK.md`

## Related Documents

- `docs/runbooks/GO_LIVE_CHECKLIST.md` — step-by-step go-live procedure
- `docs/runbooks/GO_LIVE_REHEARSAL.md` — rehearsal runbook
- `docs/runbooks/ROLLBACK_RUNBOOK.md` — rollback procedure
- `docs/runbooks/KILL_SWITCH.md` — emergency halt operations
- `docs/runbooks/INCIDENT_RESPONSE.md` — incident response
- `docs/runbooks/PRODUCTION_DRY_RUN_VERIFICATION.md` — dry-run reference
- `docs/releases/PHASE37_RELEASE_READINESS.md` — release readiness
- `docs/releases/PHASE41_RELEASE_CANDIDATE.md` — current release candidate
- `Makefile` — all `prod-*`, `go-live-*`, and `release-*` targets
