#!/usr/bin/env bash
set -euo pipefail

if [[ ! -d "/opt/zdash/runtime" ]]; then
  echo "Production runtime not found at /opt/zdash/runtime"
  echo "Run: sudo ./install-zdash-prod.sh"
  exit 1
fi

echo "Stopping production stack..."
sudo systemctl stop zdash
sleep 1
sudo systemctl status --no-pager zdash 2>&1 || true
echo "Production stack stopped."
