#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/.runtime"
LOGS_DIR="$RUNTIME_DIR/logs"
PIDS_DIR="$RUNTIME_DIR/pids"
BACKEND_PORT="${BACKEND_PORT:-8005}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
NODE_VERSION="${NODE_VERSION:-20}"

mkdir -p "$LOGS_DIR" "$PIDS_DIR"

clean_stale_pid() {
  local pid_file="$1"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid=$(cat "$pid_file")
    if ! kill -0 "$pid" 2>/dev/null; then
      rm -f "$pid_file"
    fi
  fi
}

check_running() {
  local pid_file="$1"
  local name="$2"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid=$(cat "$pid_file")
    if kill -0 "$pid" 2>/dev/null; then
      echo "$name is already running (PID $pid)"
      return 0
    fi
    rm -f "$pid_file"
  fi
  return 1
}

clean_stale_pid "$PIDS_DIR/backend.pid"
clean_stale_pid "$PIDS_DIR/frontend.pid"

if check_running "$PIDS_DIR/backend.pid" "Backend"; then
  BACKEND_ALREADY=true
else
  BACKEND_ALREADY=false
fi

if check_running "$PIDS_DIR/frontend.pid" "Frontend"; then
  FRONTEND_ALREADY=true
else
  FRONTEND_ALREADY=false
fi

if $BACKEND_ALREADY && $FRONTEND_ALREADY; then
  echo "Both servers are already running."
  exit 0
fi

# Start backend
if ! $BACKEND_ALREADY; then
  cd "$ROOT_DIR/backend"
  if [[ -f .venv/bin/activate ]]; then
    source .venv/bin/activate
  fi
  nohup uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" \
    > "$LOGS_DIR/backend.log" 2>&1 &
  echo $! > "$PIDS_DIR/backend.pid"
  echo "Backend starting (PID $(cat "$PIDS_DIR/backend.pid"))..."
fi

# Start frontend
if ! $FRONTEND_ALREADY; then
  cd "$ROOT_DIR/frontend"
  if command -v nvm &>/dev/null; then
    nvm use "$NODE_VERSION" 2>/dev/null || true
  fi
  nohup npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT" \
    > "$LOGS_DIR/frontend.log" 2>&1 &
  echo $! > "$PIDS_DIR/frontend.pid"
  echo "Frontend starting (PID $(cat "$PIDS_DIR/frontend.pid"))..."
fi

# Wait for health
echo ""
sleep 2
if curl -sf "http://localhost:$BACKEND_PORT/health" >/dev/null 2>&1; then
  echo "Backend health: OK"
else
  echo "Backend health: waiting..."
fi

LAN_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")

echo ""
echo "=== Local URLs ==="
echo "Backend  : http://localhost:$BACKEND_PORT"
echo "API Docs : http://localhost:$BACKEND_PORT/docs"
echo "Frontend : http://localhost:$FRONTEND_PORT"
echo "LAN Backend  : http://$LAN_IP:$BACKEND_PORT"
echo "LAN Frontend : http://$LAN_IP:$FRONTEND_PORT"
echo ""
echo "Logs:"
echo "  Backend  : $LOGS_DIR/backend.log"
echo "  Frontend : $LOGS_DIR/frontend.log"
echo "  PIDs     : $PIDS_DIR/"
