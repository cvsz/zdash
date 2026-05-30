# Final Release Runbook

## Preflight

- [ ] Release branch is up to date with `main`
- [ ] `.env.production` generated (`make prod-env-generate`)
- [ ] All secrets rotated from defaults
- [ ] Backend and frontend dependencies installed
- [ ] No uncommitted changes (`git status --short` clean)
- [ ] Release tag determined (e.g. `v2.0.1`)

## 1. Environment setup

```bash
make prod-env-generate
# Edit .env.production with real secrets
```

## 2. Dependency install

```bash
# Backend
cd backend && pip install -r requirements.txt && cd ..

# Frontend
make frontend-install
```

## 3. Backend validation

```bash
# Lint
make backend-lint

# Tests
make backend-test
```

## 4. Frontend validation

```bash
# Tests
make frontend-test

# Production build
make frontend-build
```

## 5. Docker validation

```bash
# Compose config
docker compose -f docker-compose.prod.yml config

# Build images
make docker-build
```

## 6. Security validation

```bash
# Full safety scan
make safety-scan

# Production safety check
curl http://localhost:8005/api/admin/safety-check

# Check .env matches .env.example
diff <(sort .env.example) <(sort .env) || echo "env files differ — review"
```

## 7. Release tagging

```bash
make release-tag RELEASE_TAG=v2.0.1
```

## 8. Rollback steps

If the release fails:
1. `make prod-down`
2. Rollback deployment to prior image.
3. Restore database from backup.
4. Verify with `make prod-health`.
5. Run incident response if needed.

## 9. Post-release monitoring

- Check `/health` endpoint returns 200.
- Verify frontend loads at expected URL.
- Monitor logs for errors.
- Watch alert rules for safety triggers.
- Confirm dry-run mode active.
