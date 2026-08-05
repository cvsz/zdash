#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="${ZDASH_COMPOSE_FILE:-$ROOT/docker-compose.yml}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-zdash-local}"
ZDASH_BIND_ADDRESS="${ZDASH_BIND_ADDRESS:-127.0.0.1}"
ZDASH_HTTP_PORT="${ZDASH_HTTP_PORT:-18080}"
WAIT_TIMEOUT="${ZDASH_WAIT_TIMEOUT:-240}"

log() {
  printf '\n[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

die() {
  printf '\n[ERROR] %s\n' "$*" >&2
  exit 1
}

select_docker() {
  if docker info >/dev/null 2>&1; then
    DOCKER=(docker)
    return
  fi

  if command -v sudo >/dev/null 2>&1 && sudo docker info >/dev/null 2>&1; then
    DOCKER=(sudo docker)
    return
  fi

  die "Docker is unavailable. Start Docker or grant this user Docker access."
}

select_docker

compose() {
  COMPOSE_PROJECT_NAME="$COMPOSE_PROJECT_NAME" \
  ZDASH_BIND_ADDRESS="$ZDASH_BIND_ADDRESS" \
  ZDASH_HTTP_PORT="$ZDASH_HTTP_PORT" \
    "${DOCKER[@]}" compose -f "$COMPOSE_FILE" "$@"
}

gateway_running() {
  local container_id
  container_id="$(compose ps -q gateway 2>/dev/null || true)"
  [ -n "$container_id" ] &&
    [ "$("${DOCKER[@]}" inspect -f '{{.State.Running}}' "$container_id" 2>/dev/null || true)" = "true" ]
}

assert_port_available() {
  gateway_running && return

  if command -v ss >/dev/null 2>&1 &&
     ss -ltnH "sport = :$ZDASH_HTTP_PORT" 2>/dev/null | grep -q .; then
    ss -ltnp "sport = :$ZDASH_HTTP_PORT" 2>/dev/null || true
    die "${ZDASH_BIND_ADDRESS}:${ZDASH_HTTP_PORT} is already in use. Set ZDASH_HTTP_PORT to a free loopback port."
  fi
}

wait_without_compose_wait() {
  local elapsed=0
  local container_id status

  while [ "$elapsed" -lt "$WAIT_TIMEOUT" ]; do
    container_id="$(compose ps -q gateway 2>/dev/null || true)"
    if [ -n "$container_id" ]; then
      status="$("${DOCKER[@]}" inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container_id" 2>/dev/null || true)"
      if [ "$status" = "healthy" ]; then
        return 0
      fi
      if [ "$status" = "exited" ] || [ "$status" = "dead" ]; then
        return 1
      fi
    fi
    sleep 5
    elapsed=$((elapsed + 5))
  done

  return 1
}

start_stack() {
  assert_port_available
  log "Building and starting $COMPOSE_PROJECT_NAME"

  if compose up --help 2>&1 | grep -q -- '--wait'; then
    compose up -d --build --wait --wait-timeout "$WAIT_TIMEOUT"
  else
    compose up -d --build
    wait_without_compose_wait || {
      compose ps || true
      compose logs --no-color --tail=200 || true
      die "Local stack did not become healthy within ${WAIT_TIMEOUT}s."
    }
  fi

  health_stack
}

health_stack() {
  log "Service status"
  compose ps

  log "Gateway health"
  curl -fsS "http://${ZDASH_BIND_ADDRESS}:${ZDASH_HTTP_PORT}/gateway-health"
  printf '\n'

  log "Backend health through the gateway"
  curl -fsS "http://${ZDASH_BIND_ADDRESS}:${ZDASH_HTTP_PORT}/health"
  printf '\n'

  log "zDash local URL: http://${ZDASH_BIND_ADDRESS}:${ZDASH_HTTP_PORT}"
}

case "${1:-up}" in
  up|start)
    start_stack
    ;;
  build)
    compose build --pull
    ;;
  health|status)
    health_stack
    ;;
  logs)
    shift || true
    compose logs -f --tail=200 "$@"
    ;;
  restart)
    compose restart
    health_stack
    ;;
  down|stop)
    compose down --remove-orphans
    ;;
  reset)
    [ "${CONFIRM_RESET:-no}" = "yes" ] ||
      die "Set CONFIRM_RESET=yes to remove containers and local data volumes."
    compose down --remove-orphans --volumes
    ;;
  config)
    compose config
    ;;
  *)
    cat >&2 <<'EOF'
Usage: bash scripts/local/stack.sh [up|build|health|status|logs|restart|down|reset|config]

Defaults:
  COMPOSE_PROJECT_NAME=zdash-local
  ZDASH_BIND_ADDRESS=127.0.0.1
  ZDASH_HTTP_PORT=18080

Examples:
  bash scripts/local/stack.sh up
  ZDASH_HTTP_PORT=18081 bash scripts/local/stack.sh up
  bash scripts/local/stack.sh logs backend
  CONFIRM_RESET=yes bash scripts/local/stack.sh reset
EOF
    exit 2
    ;;
esac
