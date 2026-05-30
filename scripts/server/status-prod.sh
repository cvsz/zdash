#!/usr/bin/env bash
set -euo pipefail

if [[ ! -d "/opt/zdash/runtime" ]]; then
  echo "Production runtime not found at /opt/zdash/runtime"
  echo "Run: sudo ./install-zdash-prod.sh"
  exit 1
fi

echo "=== Production Status ==="
echo ""
echo "--- Systemd Status ---"
sudo systemctl status --no-pager zdash 2>&1 || true

echo ""
COMPOSE_DIR="/opt/zdash"
if [[ -f "$COMPOSE_DIR/docker-compose.yml" ]]; then
  echo "--- Docker Compose ---"
  (cd "$COMPOSE_DIR" && docker compose ps 2>/dev/null) || echo "(docker compose not available)"
fi

echo ""
if [[ -f "/opt/zdash/runtime/scripts/zdash-health.sh" ]]; then
  echo "--- Health ---"
  bash "/opt/zdash/runtime/scripts/zdash-health.sh" || true
fi
