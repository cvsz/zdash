#!/usr/bin/env bash
set -euo pipefail

echo "Initiating rollback..."

if [ "${ROLLBACK_CONFIRM:-no}" != "yes" ]; then
  echo "ERROR: ROLLBACK_CONFIRM=yes is required"
  exit 1
fi

echo "Rolling back to previous state..."
# Placeholder for actual rollback logic
# e.g., restoring previous image tags or scaling back up previous deployment

echo "Running smoke test post-rollback..."
./infra/scripts/k8s-smoke-test.sh

echo "Rollback complete."
