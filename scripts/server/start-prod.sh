#!/usr/bin/env bash
set -euo pipefail

RUNTIME_DIR="/opt/zdash/runtime"

if [[ ! -d "$RUNTIME_DIR" ]]; then
  echo "Production runtime not found at $RUNTIME_DIR"
  echo "Run: sudo ./install-zdash-prod.sh"
  exit 1
fi

echo "Starting production stack..."
sudo systemctl start zdash
sleep 2
sudo systemctl status --no-pager zdash

echo ""
if [[ -f "$RUNTIME_DIR/scripts/zdash-health.sh" ]]; then
  bash "$RUNTIME_DIR/scripts/zdash-health.sh" || true
fi
