# Deployment Runbook

## Pre-deployment Checklist
1. Ensure all tests pass (`npm test`, `pytest`).
2. Build and tag new Docker images.
3. Run Cloudflare dry-run script.

## Deployment Steps
1. Run database migrations using Alembic.
2. Update Kubernetes deployments with new image tags.
3. Monitor the rollout status (`kubectl rollout status`).

## Rollback
If issues are detected, execute `infra/scripts/rollback.sh`.
