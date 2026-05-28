#!/usr/bin/env bash
set -euo pipefail

echo "Deploying to production environment..."

if [ "${DEPLOY_CONFIRM:-no}" != "yes" ]; then
  echo "ERROR: DEPLOY_CONFIRM=yes is required"
  exit 1
fi

if [ "${APP_ENV:-}" != "production" ]; then
  echo "ERROR: APP_ENV=production is required"
  exit 1
fi

if [ "${PRODUCTION_SAFETY_LOCK:-true}" == "true" ]; then
  echo "ERROR: PRODUCTION_SAFETY_LOCK is enabled. Cannot deploy."
  exit 1
fi

echo "Building/Pulling images..."
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml pull

echo "Starting services..."
docker compose -f docker-compose.prod.yml up -d

echo "Running migrations..."
docker compose -f docker-compose.prod.yml exec -T backend alembic upgrade head || echo "No migrations or migration failed"

echo "Running smoke test..."
./infra/scripts/k8s-smoke-test.sh

echo "Production deployment complete."
