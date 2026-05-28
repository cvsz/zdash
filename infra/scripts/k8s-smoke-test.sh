#!/usr/bin/env bash
set -euo pipefail

echo "Running Smoke Tests..."
# Simple curl check or basic health endpoint validation
if curl -s -f http://localhost:8005/api/health; then
  echo "Backend health check passed."
else
  echo "Backend health check failed."
fi
echo "Smoke tests complete."
