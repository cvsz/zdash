#!/usr/bin/env bash
set -euo pipefail

echo "Deploying to development environment..."

# Start services
docker compose up --build -d

# Run migrations (assuming backend container exists)
echo "Running database migrations..."
docker compose exec -T backend alembic upgrade head || echo "No migrations to run or migration failed (check logs)"

# Run smoke test
if [ -f ./infra/scripts/k8s-smoke-test.sh ]; then
  ./infra/scripts/k8s-smoke-test.sh
else
  echo "Smoke test script not found."
fi

echo "Development deployment complete."
