# Production Dry-Run Verification

## Purpose

Run a full production deployment dry-run against a local or CI environment to verify that all runtime, health, rollback, and observability prerequisites are satisfied without enabling live trading, real external mutations, or exposing secrets.

## Safety

- No real broker execution is enabled.
- No real social posting is enabled.
- No real IoT mutation is enabled.
- No secrets are printed at any step.
- All checks are read-only.
- `DRY_RUN=true` is verified as a runtime invariant.

## Prerequisites

- Project repository cloned and dependencies installed.
- `make validate-fast` passes.
- `scripts/prod/` exists with executable verification scripts.

## Verification Layers

### Layer 1: Production Runtime

Checks that the production runtime directory exists at `/opt/zdash/runtime` and contains all required components.

```bash
bash scripts/prod/verify-prod-runtime.sh
```

Verifies:
- Runtime directory exists
- `zdash.service` systemd unit file exists
- Docker Compose config file exists
- `.env.production` exists (without printing values)
- Health helper script exists
- Logs helper script exists
- Backup helper script exists
- Update helper script exists

If runtime is not found, the script exits with:
```
Production runtime not found at /opt/zdash/runtime
Run: sudo ./install-zdash-prod.sh
```

### Layer 2: Production Health

Checks that all services are healthy and responding.

```bash
bash scripts/prod/verify-prod-health.sh
```

Verifies:
- Backend health endpoint (`/health`) responds HTTP 200
- Backend safety check (`/api/admin/safety-check`) passes
- Frontend responds HTTP 200
- Risk system endpoint is operational
- Backend port 8005 is listening
- Frontend port 5173 is listening (or nginx runtime exposure)

### Layer 3: Rollback Readiness

Checks that safety env values, rollback documentation, and release artifacts are in place.

```bash
bash scripts/prod/verify-prod-rollback-readiness.sh
```

Verifies:
- `DRY_RUN=true`
- `LIVE_TRADING_ACK=false`
- `MT5_ENABLED=false`
- `PRODUCTION_ALLOW_LIVE_ACTIONS=false`
- `RISK_GUARDIAN_ENABLED=true`
- Backend port is 8005
- Rollback runbook exists
- Release readiness report exists with status GO
- Go-live checklist exists
- Production dry-run verification doc exists

### Layer 4: Observability

Checks that observability, monitoring, and operational runbooks are documented.

```bash
bash scripts/prod/verify-prod-observability.sh
```

Verifies:
- Realtime endpoints documented in `REALTIME_GATEWAY.md`
- Observability runbook exists
- Incident response runbook exists
- Kill switch runbook exists
- Risk halt runbook exists
- Backup/restore runbook exists
- Deployment runbook exists
- DB migration runbook exists
- Docker Compose config is valid (production and local)
- Logs helper is executable

## Makefile Targets

```bash
# Full production dry-run (all layers)
make prod-verify

# Health layer only
make prod-verify-health

# Rollback readiness layer only
make prod-verify-rollback

# Observability layer only
make prod-verify-observability

# Phase 39 validation gate
make phase39-validate
```

## Interpreting Results

- All checks must pass before a production deployment is attempted.
- Any failure should be investigated and resolved before proceeding.
- If the production runtime is not installed, the scripts fail safely with a clear message.
- Secrets are never printed — only the presence or absence of `.env.production` is reported.

## Failure Handling

| Failure | Action |
|---------|--------|
| Runtime not found | Run `sudo ./install-zdash-prod.sh` |
| Service unhealthy | Check `make prod-logs` for error details |
| Safety env misconfigured | Update `.env.production` with correct values |
| Documentation missing | Create missing documentation per runbook templates |
| Compose config invalid | Run `docker compose config` and fix syntax errors |

## Related Documents

- `docs/runbooks/GO_LIVE_CHECKLIST.md` — step-by-step go-live procedure
- `docs/runbooks/ROLLBACK_RUNBOOK.md` — rollback procedure
- `docs/releases/PHASE37_RELEASE_READINESS.md` — release readiness status
- `Makefile` — `prod-*` and `phase39-*` targets
