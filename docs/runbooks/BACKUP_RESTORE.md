# BACKUP_RESTORE

## Purpose
Backup and restore DB/config safely.

## Prerequisites
- `pg_dump`/`psql` available for PostgreSQL

## Commands
```bash
./scripts/backup-db.sh
./scripts/backup-config.sh
./scripts/verify-backup.sh <backup-file>
./scripts/restore-db.sh <backup-file>
```

## Expected output
- Timestamped backup files in `./backups`.

## Failure handling
- Verify backup integrity before restore.

## Rollback steps
- Restore previous known-good backup.

## Safety notes
- Config backup excludes secrets unless `ALLOW_SECRETS=true`.
