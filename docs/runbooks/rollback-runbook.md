# Rollback Runbook

## When to rollback

- Validation check failed after deploy.
- Error rate spikes above threshold.
- User-facing regression confirmed.
- Database migration introduced data loss.
- Security vulnerability discovered.

## How to stop services

```bash
make prod-down
# Or manually:
docker compose -f docker-compose.prod.yml down
```

## How to revert release

1. Identify the prior stable image tag:
   ```bash
   docker images zdash-backend
   ```
2. Update tag in `docker-compose.prod.yml` or re-tag image:
   ```bash
   docker tag zdash-backend:previous zdash-backend:latest
   ```
3. Restart:
   ```bash
   make prod-up
   ```

## How to restore database

```bash
# List backups
ls -la ./backups/

# Restore
./scripts/restore-db.sh <backup-file>
```

## How to verify recovery

```bash
# Health check
curl http://localhost:8005/health

# Safety check
curl http://localhost:8005/api/admin/safety-check

# Frontend loads
curl http://localhost:5173
```

## How to communicate incident

1. Notify ops channel.
2. File incident report in `docs/runbooks/incident-response-runbook.md`.
3. Conduct RCA before re-deploy.

## Safety notes

- Trigger emergency halt before rollback during active incidents.
- Never rollback without a confirmed backup.
- Verify database rollback completed before restarting services.
