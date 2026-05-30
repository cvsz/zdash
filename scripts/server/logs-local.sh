#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
LOGS_DIR="$ROOT_DIR/.runtime/logs"
SERVICE="${SERVICE:-}"

show_log() {
  local log_file="$1"
  local name="$2"
  if [[ -f "$log_file" ]]; then
    echo "=== $name ==="
    tail -f "$log_file"
  else
    echo "No $name log file at $log_file"
    exit 1
  fi
}

if [[ "$SERVICE" == "backend" ]]; then
  show_log "$LOGS_DIR/backend.log" "Backend"
elif [[ "$SERVICE" == "frontend" ]]; then
  show_log "$LOGS_DIR/frontend.log" "Frontend"
elif [[ -z "$SERVICE" ]]; then
  if [[ -f "$LOGS_DIR/backend.log" ]]; then
    echo "=== Backend Log ==="
    tail -f "$LOGS_DIR/backend.log" &
    BG_PID=$!
  fi
  if [[ -f "$LOGS_DIR/frontend.log" ]]; then
    echo "=== Frontend Log ==="
    tail -f "$LOGS_DIR/frontend.log" &
    FG_PID=$!
  fi
  if [[ -z "${BG_PID:-}" && -z "${FG_PID:-}" ]]; then
    echo "No log files found at $LOGS_DIR/"
    exit 1
  fi
  trap 'kill ${BG_PID:-} ${FG_PID:-} 2>/dev/null; exit' INT TERM
  wait
else
  echo "Usage: SERVICE=backend|frontend $0"
  echo "  or:  $0  (follows both)"
  exit 1
fi
