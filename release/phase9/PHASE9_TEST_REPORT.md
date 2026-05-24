# PHASE9_TEST_REPORT

## Backend test result
Command:
```bash
cd backend
pytest -q
```
Result:
- Failed in this environment: `/bin/bash: pytest: command not found`
- Verified with project venv:
  - `cd backend && ../.venv/bin/pytest -q`
  - `37 passed, 1 warning`

## Frontend build result
Command:
```bash
cd frontend
npm install
npm run build
```
Result:
- Build passed (`vite` output generated dist assets)

## Alembic migration result
Command:
```bash
cd backend
alembic -c alembic.ini upgrade head
```
Result:
- Failed in this environment when run as `alembic upgrade head`: `/bin/bash: alembic: command not found`
- Verified with project venv:
  - `cd backend && ../.venv/bin/alembic -c alembic.ini upgrade head`
  - Upgrade to head succeeded.

## Docker compose validation result
Commands:
```bash
docker compose config
docker compose --profile observability config
```
Result:
- Both commands succeeded.

## Security scan result
Commands:
```bash
.venv/bin/pip-audit
cd frontend && npm audit --audit-level=high
rg secret patterns (excluding .venv)
```
Results:
- `pip-audit`: no known vulnerabilities for resolved dependencies (local package skipped as expected).
- `npm audit`: 2 moderate vulnerabilities in `vite/esbuild` chain; no high/critical.
- Secret pattern scan: no hits in project files (after excluding `.venv`).
