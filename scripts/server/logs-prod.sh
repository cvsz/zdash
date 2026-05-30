#!/usr/bin/env bash
set -euo pipefail

if [[ ! -d "/opt/zdash/runtime" ]]; then
  echo "Production runtime not found at /opt/zdash/runtime"
  echo "Run: sudo ./install-zdash-prod.sh"
  exit 1
fi

SERVICE="${SERVICE:-backend}"

if [[ -f "/opt/zdash/runtime/scripts/zdash-logs.sh" ]]; then
  exec bash "/opt/zdash/runtime/scripts/zdash-logs.sh" "$SERVICE"
else
  echo "Production log helper not found at /opt/zdash/runtime/scripts/zdash-logs.sh"
  echo "Supported services: backend, nginx, frontend, postgres, redis"
  exit 1
fi
