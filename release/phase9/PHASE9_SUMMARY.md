# PHASE9_SUMMARY

## What changed
Phase 9 added release verification, observability, CI/CD workflows, security hardening docs/controls, API contract verification, runbooks, backup/restore scripts, and release packaging artifacts.

## Why it changed
To move zDash from production-capable code to release-ready and auditable operations with reproducible verification paths.

## How to run
```bash
./scripts/setup-dev.sh
source .venv/bin/activate
./scripts/migrate-db.sh
cd backend && uvicorn app.main:app --reload
cd frontend && npm run dev
```

## How to test
```bash
cd backend && ../.venv/bin/pytest -q
cd backend && ../.venv/bin/alembic -c alembic.ini upgrade head
cd frontend && npm install && npm run build
docker compose config
docker compose --profile observability config
```

## How to deploy
```bash
cp .env.production.example .env.production
# set real secrets and safe gate values

docker compose --profile production up -d --build
```

## How to rollback
```bash
./scripts/backup-db.sh
./scripts/rollback-db.sh
# restore if needed
./scripts/restore-db.sh <backup-file>
```

## Known limitations
- MT5/Tapo are adapter shells.
- SSE auth uses query token for EventSource compatibility.
- In-process rate limiter should be replaced with Redis-backed limiter for multi-node deployments.
- Workspace is not a Git repository, so native `git diff` patch export is unavailable here.

## Next recommended phase
Phase 10: distributed rate limiting + real adapter implementations + canary rollout + SLO/error-budget governance.
