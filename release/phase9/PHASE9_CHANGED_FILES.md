# PHASE9_CHANGED_FILES

## Backend core
- backend/app/core/observability.py
- backend/app/core/middleware.py
- backend/app/core/auth.py
- backend/app/core/audit.py
- backend/app/core/config.py
- backend/app/core/database.py
- backend/app/core/events.py
- backend/app/core/logging.py
- backend/app/main.py

## Backend API / domain
- backend/app/api/auth.py
- backend/app/api/audit.py
- backend/app/api/logs.py
- backend/app/api/trading.py
- backend/app/api/risk.py
- backend/app/api/scheduler.py
- backend/app/api/content.py
- backend/app/api/backtesting.py
- backend/app/api/agents.py
- backend/app/api/health.py
- backend/app/trading/mt5_adapter.py
- backend/app/trading/execution_engine.py
- backend/app/risk/halt_flag.py
- backend/app/scheduler/jobs.py
- backend/app/content/pipeline.py
- backend/app/iot/tapo_adapter.py

## Persistence
- backend/app/models/entities.py
- backend/app/models/__init__.py
- backend/app/repositories/store.py
- backend/app/repositories/__init__.py
- backend/alembic.ini
- backend/alembic/env.py
- backend/alembic/versions/20260524_0003_phase8_persistence.py

## Tests
- backend/tests/test_api_contracts.py
- backend/tests/test_auth_rbac.py
- backend/tests/test_repositories.py
- backend/tests/test_persistence_features.py
- backend/tests/test_lifespan.py
- backend/tests/test_migrations.py
- backend/tests/test_frontend_build_contract.py
- backend/tests/conftest.py
- backend/tests/* existing updated files

## Frontend
- frontend/src/api/client.ts
- frontend/src/api/contracts.ts
- frontend/src/App.tsx
- frontend/src/components/ErrorBoundary.tsx
- frontend/src/components/EnvBadge.tsx
- frontend/src/components/LiveModeBanner.tsx
- frontend/src/components/OfflineBanner.tsx
- frontend/src/components/RoleGate.tsx
- frontend/src/components/BuildInfo.tsx
- frontend/src/components/Layout.tsx
- frontend/src/pages/Login.tsx
- frontend/src/pages/AuditLogs.tsx
- frontend/src/pages/SessionLogs.tsx
- frontend/src/pages/RiskPanel.tsx
- frontend/src/pages/XauDashboard.tsx
- frontend/src/pages/ContentPipeline.tsx
- frontend/src/pages/Scheduler.tsx
- frontend/src/pages/Dashboard.tsx

## DevOps / deploy
- .github/workflows/backend-ci.yml
- .github/workflows/frontend-ci.yml
- .github/workflows/docker-ci.yml
- .github/workflows/security-ci.yml
- .github/workflows/release-check.yml
- docker-compose.yml
- backend/Dockerfile
- frontend/Dockerfile
- deploy/nginx/default.conf
- deploy/prometheus/prometheus.yml
- deploy/grafana/provisioning/datasources/prometheus.yml
- deploy/grafana/provisioning/dashboards/zdash.yml
- deploy/grafana/dashboards/zdash-overview.json

## Scripts / docs / release
- scripts/backup-db.sh
- scripts/restore-db.sh
- scripts/backup-config.sh
- scripts/verify-backup.sh
- scripts/migrate-db.sh
- scripts/rollback-db.sh
- scripts/smoke-test.sh
- docs/audits/PHASE9_RELEASE_AUDIT.md
- docs/security/SECURITY_REVIEW.md
- docs/security/RBAC_MATRIX.md
- docs/security/LIVE_TRADING_SAFETY.md
- docs/runbooks/*.md
- release/phase9/*
- README.md
- .env.example
- .env.production.example
- backend/pyproject.toml
