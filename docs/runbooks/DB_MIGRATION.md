# DB_MIGRATION

## Purpose
Apply/verify schema changes via Alembic.

## Prerequisites
- `.venv` active
- `DATABASE_URL` configured

## Commands
```bash
./scripts/migrate-db.sh
cd backend && alembic -c alembic.ini current
```

## Expected output
- Head revision `20260524_0003`.

## Failure handling
- Inspect migration logs and DB connectivity.

## Rollback steps
```bash
./scripts/rollback-db.sh
```

## Safety notes
- Backup before migrating in production.
