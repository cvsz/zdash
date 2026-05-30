# Rollback Runbook

> Note: This file is maintained at `docs/runbooks/rollback-runbook.md` (preferred). This copy exists for backward compatibility.

## When to rollback

- Validation check failed after deploy.
- Error rate spikes above threshold.
- User-facing regression confirmed.
- Database migration introduced data loss.
- Security vulnerability discovered.

## Commands

```bash
./scripts/backup-db.sh
./scripts/rollback-db.sh
```

## Prerequisites

- Recent backups
- Release artifact references

## Rollback steps

1. `make prod-down`
2. Revert deployment to prior image/build:
   ```bash
   docker tag zdash-backend:previous zdash-backend:latest
   ```
3. Restore database if needed:
   ```bash
   ./scripts/restore-db.sh <backup-file>
   ```
4. `make prod-up`

## Verification

```bash
curl http://localhost:8005/health
curl http://localhost:8005/api/admin/safety-check
```

## Failure handling

- If rollback fails, restore from backup.
- If API unavailable, stop at orchestrator level.

## Safety notes

- Trigger emergency halt before rollback during incidents.
- Never rollback without a confirmed backup.
- Verify recovery before declaring incident resolved.
