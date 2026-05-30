#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PIDS_DIR="$ROOT_DIR/.runtime/pids"

stop_service() {
  local pid_file="$1"
  local name="$2"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid=$(cat "$pid_file")
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      echo "Stopped $name (PID $pid)"
    else
      echo "$name not running (stale PID file cleaned)"
    fi
    rm -f "$pid_file"
  else
    echo "$name not running"
  fi
}

stop_service "$PIDS_DIR/backend.pid" "Backend"
stop_service "$PIDS_DIR/frontend.pid" "Frontend"

echo "All local servers stopped."
