# Production backend recovery

## Symptom

The production build completes, PostgreSQL and Redis become healthy, but `zdash-backend` remains unhealthy and Docker Compose stops dependent services.

## Root cause

The previous production installer generated a new `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, `JWT_SECRET_KEY`, and bootstrap-admin password on every invocation. A PostgreSQL password supplied through the container environment is used during first-time database initialization only; changing that environment value does not update the role password stored in an existing persistent volume.

This can produce the following state:

- PostgreSQL health passes because `pg_isready` verifies server readiness without authenticating the application connection.
- The backend receives the newly generated password.
- The persistent PostgreSQL role still has the previous password.
- Backend startup and migrations fail, so the backend healthcheck never succeeds.

## Fixed installer behavior

`install-zdash-prod.sh` now acts as a safe recovery wrapper around the original implementation. It:

1. Loads an allowlist of existing values from `/opt/zdash/runtime/.env.production`.
2. Exports those values before invoking the original installer, preventing unintended secret rotation.
3. Reconciles the PostgreSQL role password with the protected runtime value.
4. Restarts the backend and waits for Docker health.
5. Captures backend, PostgreSQL, Redis, Compose, and container-state diagnostics when recovery fails.
6. Stores pre-recovery copies of the runtime environment and Compose file with restrictive permissions.

The original implementation is materialized locally from commit `b015e7980edd1677649aa56f6bc59f032ee47a38` as `install-zdash-prod-legacy.sh` and excluded through `.git/info/exclude`.

## Run a normal safe install/update

```bash
make install-prod ZDASH_DOMAIN=zdash.zeaz.dev
```

## Repair the current stack without rebuilding

```bash
sudo ZDASH_DOMAIN=zdash.zeaz.dev ./install-zdash-prod.sh --repair-only
```

## Validate

```bash
sudo docker compose \
  --env-file /opt/zdash/runtime/.env.production \
  -f /opt/zdash/runtime/docker-compose.yml ps

sudo docker logs --tail=200 zdash-backend
curl -kfsS https://127.0.0.1/health
```

Recovery diagnostics are written to `/opt/zdash/logs/recovery/`. Database, Redis, JWT, and bootstrap-admin secrets are not printed.
