#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
BACKEND_PORT="${BACKEND_PORT:-8005}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

LAN_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")

echo "=== Local URLs ==="
echo "Backend  : http://localhost:$BACKEND_PORT"
echo "API Docs : http://localhost:$BACKEND_PORT/docs"
echo "Frontend : http://localhost:$FRONTEND_PORT"
echo "LAN Backend  : http://$LAN_IP:$BACKEND_PORT"
echo "LAN Frontend : http://$LAN_IP:$FRONTEND_PORT"

if [[ "${OPEN_BROWSER:-false}" == "true" ]] && command -v xdg-open &>/dev/null; then
  echo ""
  echo "Opening frontend URL in browser..."
  xdg-open "http://localhost:$FRONTEND_PORT"
fi
