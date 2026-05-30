#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PIDS_DIR="$ROOT_DIR/.runtime/pids"
BACKEND_PORT="${BACKEND_PORT:-8005}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

echo "=== Local Server Status ==="
echo ""

show_pid_status() {
  local pid_file="$1"
  local name="$2"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid=$(cat "$pid_file")
    if kill -0 "$pid" 2>/dev/null; then
      echo "$name: RUNNING (PID $pid)"
    else
      echo "$name: STOPPED (stale PID $pid)"
    fi
  else
    echo "$name: STOPPED"
  fi
}

show_pid_status "$PIDS_DIR/backend.pid" "Backend"
show_pid_status "$PIDS_DIR/frontend.pid" "Frontend"

echo ""
echo "=== Port Status ==="
for port in "$BACKEND_PORT" "$FRONTEND_PORT"; do
  if ss -tlnp "sport = :$port" 2>/dev/null | grep -q ":$port"; then
    echo "Port $port: LISTENING"
  else
    echo "Port $port: CLOSED"
  fi
done

echo ""
echo "=== Health Check ==="
if curl -sf "http://localhost:$BACKEND_PORT/health" >/dev/null 2>&1; then
  echo "Backend /health: OK"
else
  echo "Backend /health: UNREACHABLE"
fi

FRONTEND_STATUS=$(curl -sf -o /dev/null -w "%{http_code}" "http://localhost:$FRONTEND_PORT" 2>/dev/null || echo "000")
if [[ "$FRONTEND_STATUS" != "000" ]]; then
  echo "Frontend HTTP: $FRONTEND_STATUS"
else
  echo "Frontend HTTP: UNREACHABLE"
fi

echo ""
LAN_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")
echo "LAN IP: $LAN_IP"
echo "Backend URL : http://$LAN_IP:$BACKEND_PORT"
echo "Frontend URL: http://$LAN_IP:$FRONTEND_PORT"
