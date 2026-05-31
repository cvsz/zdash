# Rollback Runbook

## Purpose
Standard operating procedure for rolling back a zDash release to a prior stable state.

## When to Rollback

- Validation check failed after deploy (health, safety, or smoke test).
- Error rate spikes above configured threshold.
- User-facing regression confirmed by manual or automated testing.
- Database migration introduced data loss or schema corruption.
- Security vulnerability discovered post-deploy.
- Incident triage determines rollback is faster than hotfix.

## Prerequisites

- Access to Docker host and Docker Compose configuration.
- Prior stable Docker image tags identified.
- Database backup from pre-deploy state (see `docs/runbooks/BACKUP_RESTORE.md`).
- Release artifact references for prior version (see `docs/releases/`).

## Step 1: Halt

Before rolling back, halt automated trading and risk-sensitive operations:

```bash
# Emergency halt (stops all trading activity)
curl -X POST http://localhost:8005/api/risk/emergency-halt

# Or via Makefile if services are up
make kill-switch
```

Verify halt:
```bash
curl http://localhost:8005/api/risk/status
# Expect: {"halted": true, "locked": true}
```

## Step 2: Stop Services

```bash
make prod-down
# Or manually:
docker compose -f docker-compose.prod.yml down --timeout 30
```

## Step 3: Revert Application

```bash
# List available images
docker images zdash-backend zdash-frontend

# Re-tag the prior stable image as current
docker tag zdash-backend:<prior-tag> zdash-backend:latest
docker tag zdash-frontend:<prior-tag> zdash-frontend:latest

# Alternatively, update docker-compose.prod.yml to reference <prior-tag>
```

## Step 4: Restore Database (if needed)

```bash
# List available backups
ls -la ./backups/

# Run database restore
./scripts/restore-db.sh <backup-file>

# Verify migration state
./scripts/run-db-migrations.sh status
```

## Step 5: Restart Services

```bash
make prod-up
# Or:
docker compose -f docker-compose.prod.yml up -d
```

## Step 6: Verify Recovery

```bash
# Health check
curl http://localhost:8005/health

# Safety check
curl http://localhost:8005/api/admin/safety-check

# Frontend loads
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173

# Risk system is operational
curl http://localhost:8005/api/risk/status

# Resume halted operations if safe
curl -X POST http://localhost:8005/api/risk/resume
```

## Step 7: Communicate

1. Notify operations channel with rollback summary.
2. File incident report per `docs/runbooks/INCIDENT_RESPONSE.md`.
3. Conduct root cause analysis before re-deploying.
4. Update runbook with lessons learned.

## Failure Handling

| Failure | Action |
|---------|--------|
| Rollback script fails | Restore from backup manually; stop at orchestrator level |
| Database unreachable after restore | Restore from secondary backup; verify target database |
| API unavailable after restart | Check container logs: `docker compose logs backend` |
| Halt cannot be cleared | Admin reset required: `POST /api/risk/kill-switch-reset` |

## Safety Notes

- Trigger emergency halt before rollback during active incidents.
- Never rollback without a confirmed, tested backup.
- Verify database rollback completed before restarting services.
- Document all rollback steps with timestamps in incident report.
- If rollback succeeds but cause is unknown, keep system in halt until RCA is complete.
