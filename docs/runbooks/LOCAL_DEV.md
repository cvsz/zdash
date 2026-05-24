# LOCAL_DEV

## Purpose
Run zDash locally with SQLite and dry-run defaults.

## Prerequisites
- Python 3.11+
- Node 20+

## Commands
```bash
./scripts/setup-dev.sh
source .venv/bin/activate
./scripts/migrate-db.sh
cd backend && pytest -q
cd ../frontend && npm run build
```

## Expected output
- Backend tests pass.
- Frontend build succeeds.

## Failure handling
- If migration fails: inspect `DATABASE_URL` and rerun `./scripts/migrate-db.sh`.

## Rollback steps
- `./scripts/rollback-db.sh`

## Safety notes
- Keep `DRY_RUN=true`.
