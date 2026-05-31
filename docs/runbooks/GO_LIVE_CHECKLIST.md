# Go-Live Checklist

## Purpose
Step-by-step verification and deployment sequence for taking zDash to production.

## Pre-Flight (24h before go-live)

### Validation
- [ ] `make validate-fast` — all checks pass
- [ ] Safety scan: `make safety-scan` — no secrets leaked, no forbidden patterns
- [ ] Backend lint: `make backend-lint` — ruff passes
- [ ] Backend mypy: `cd backend && source .venv/bin/activate && mypy app --ignore-missing-imports` — zero errors
- [ ] Backend tests: `make backend-test` — all pass
- [ ] Frontend tests: `make frontend-test` — all pass
- [ ] Frontend build: `make frontend-build` — succeeds
- [ ] `docker compose -f docker-compose.yml config` — valid
- [ ] `docker compose -f docker-compose.prod.yml config` — valid

### Safety Configuration
- [ ] `.env.production` uses hardened defaults (see `.env.example`)
- [ ] `DRY_RUN=true`
- [ ] `LIVE_TRADING_ACK=false`
- [ ] `MT5_ENABLED=false`
- [ ] `PRODUCTION_ALLOW_LIVE_ACTIONS=false`
- [ ] `RISK_GUARDIAN_ENABLED=true`
- [ ] `SOCIAL_DRY_RUN=true`
- [ ] `IOT_DRY_RUN=true`
- [ ] `JWT_SECRET` and admin credentials rotated (not defaults)
- [ ] `validate_production_config()` will pass at startup

### Database
- [ ] Database backup verified (see `docs/runbooks/BACKUP_RESTORE.md`)
- [ ] Migration scripts reviewed for backward compatibility
- [ ] Rollback migration prepared (if needed)

### Documentation
- [ ] Release notes generated (see `docs/releases/`)
- [ ] Rollback runbook accessible (`docs/runbooks/ROLLBACK_RUNBOOK.md`)
- [ ] Incident response runbook accessible (`docs/runbooks/INCIDENT_RESPONSE.md`)
- [ ] Ops team briefed on go-live procedure

## Deployment

### Build and Push Images
- [ ] `make frontend-build` — production bundle compiled
- [ ] Docker images built: `docker compose build`
- [ ] Images tagged with release version
- [ ] Images pushed to registry (if applicable)

### Deploy Stack
- [ ] `make prod-down` (if upgrading from previous deployment)
- [ ] `docker compose -f docker-compose.prod.yml up -d`
- [ ] Verify all containers running: `docker compose ps`

### Run Migrations
- [ ] `./scripts/run-db-migrations.sh up`
- [ ] Verify migration applied: `./scripts/run-db-migrations.sh status`

## Post-Deployment Verification

### Service Health
- [ ] Backend health endpoint responds: `curl http://localhost:8005/health`
- [ ] Backend safety check passes: `curl http://localhost:8005/api/admin/safety-check`
- [ ] Frontend loads: `curl -s -o /dev/null -w "%{http_code}" http://localhost:5173`
- [ ] Risk system operational: `curl http://localhost:8005/api/risk/status`
- [ ] WebSocket endpoints respond (upgrade headers present)

### Smoke Tests
- [ ] Login flow works
- [ ] Dashboard loads without errors
- [ ] Trading pages show dry-run indicators
- [ ] Content pipeline shows approval-required state
- [ ] Admin pages accessible with admin role

### Monitoring
- [ ] Logs streaming without errors: `docker compose logs backend --tail 50`
- [ ] Error rate at baseline (0 — no unexpected errors)
- [ ] Metrics endpoint responding (if Prometheus configured)

## Rollback Preparedness
- [ ] Prior stable Docker image tagged and identified
- [ ] Database backup confirmed restorable
- [ ] `docs/runbooks/ROLLBACK_RUNBOOK.md` steps verified on staging

## Communication
- [ ] Ops channel notified of go-live start
- [ ] Ops channel notified of go-live completion
- [ ] Incident response team on standby for first 2 hours

## Post-Go-Live (24-48h)
- [ ] Monitor error rates
- [ ] Monitor resource usage (CPU, memory, disk)
- [ ] Verify backup schedule running
- [ ] Schedule post-go-live review

## Safety Notes

- Production blocks default weak secrets — verify `.env.production` does not use example values.
- Never skip the safety check step.
- If any validation step fails, do not proceed — roll back using `docs/runbooks/ROLLBACK_RUNBOOK.md`.
- On first deploy, confirm `validate_production_config()` passes (it raises RuntimeError on unsafe settings).
- Keep `DRY_RUN=true` for the first 24 hours of production operation.
