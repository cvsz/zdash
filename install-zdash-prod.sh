#!/usr/bin/env bash
set -Eeuo pipefail

# zDash safe production installer / recovery wrapper
# This file replaces install-zdash-prod.sh; the original installer is retained
# as install-zdash-prod-legacy.sh.
#
# Purpose:
# - preserve production secrets from the existing runtime environment
# - repair a PostgreSQL role password after an earlier installer rotated it
# - run the existing install-zdash-prod.sh without rotating persistent secrets
# - collect useful diagnostics when the backend remains unhealthy
#
# Usage:
#   sudo ZDASH_DOMAIN=zdash.zeaz.dev ./install-zdash-prod.sh
#   sudo ./install-zdash-prod.sh --repair-only
#
# Optional:
#   ZDASH_REPO=/home/cvsz/zdash
#   INSTALL_ROOT=/opt/zdash
#   RUNTIME_DIR=/opt/zdash/runtime
#   BACKEND_HEALTH_TIMEOUT=180

APP_NAME="${APP_NAME:-zdash}"
INSTALL_ROOT="${INSTALL_ROOT:-/opt/zdash}"
RUNTIME_DIR="${RUNTIME_DIR:-$INSTALL_ROOT/runtime}"
ENV_FILE="${ENV_FILE:-$RUNTIME_DIR/.env.production}"
COMPOSE_FILE="${COMPOSE_FILE:-$RUNTIME_DIR/docker-compose.yml}"
DIAG_DIR="${DIAG_DIR:-$INSTALL_ROOT/logs/recovery}"
BACKEND_HEALTH_TIMEOUT="${BACKEND_HEALTH_TIMEOUT:-180}"
BASE_INSTALLER_REF="${BASE_INSTALLER_REF:-b015e7980edd1677649aa56f6bc59f032ee47a38}"
REPAIR_ONLY=false

log() {
  printf '\n\033[1;36m[%s]\033[0m %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

warn() {
  printf '\n\033[1;33m[WARN]\033[0m %s\n' "$*" >&2
}

die() {
  printf '\n\033[1;31m[ERROR]\033[0m %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage:
  sudo ZDASH_DOMAIN=zdash.zeaz.dev ./install-zdash-prod.sh
  sudo ./install-zdash-prod.sh --repair-only

Options:
  --repair-only   Repair the current stack without running the installer.
  -h, --help      Show this help.

Environment:
  ZDASH_REPO              Path to the zDash checkout.
  INSTALL_ROOT            Default: /opt/zdash
  RUNTIME_DIR             Default: /opt/zdash/runtime
  ENV_FILE                Default: <runtime>/.env.production
  COMPOSE_FILE            Default: <runtime>/docker-compose.yml
  BACKEND_HEALTH_TIMEOUT  Default: 180 seconds
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --repair-only)
      REPAIR_ONLY=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "Unknown argument: $1"
      ;;
  esac
  shift
done

[ "${EUID:-$(id -u)}" -eq 0 ] || die "Run with sudo/root."

command -v docker >/dev/null 2>&1 || die "Docker is not installed."
docker compose version >/dev/null 2>&1 || die "Docker Compose plugin is unavailable."

resolve_repo() {
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  if [ -n "${ZDASH_REPO:-}" ]; then
    printf '%s\n' "$ZDASH_REPO"
    return
  fi

  if { [ -f "$script_dir/install-zdash-prod-legacy.sh" ] || [ -f "$script_dir/install-zdash-prod.sh" ]; } &&
     [ -d "$script_dir/backend" ] &&
     [ -d "$script_dir/frontend" ]; then
    printf '%s\n' "$script_dir"
    return
  fi

  if { [ -f "$PWD/install-zdash-prod-legacy.sh" ] || [ -f "$PWD/install-zdash-prod.sh" ]; } &&
     [ -d "$PWD/backend" ] &&
     [ -d "$PWD/frontend" ]; then
    printf '%s\n' "$PWD"
    return
  fi

  if [ -f "$INSTALL_ROOT/app/install-zdash-prod-legacy.sh" ] || [ -f "$INSTALL_ROOT/app/install-zdash-prod.sh" ]; then
    printf '%s\n' "$INSTALL_ROOT/app"
    return
  fi

  die "Cannot locate zDash checkout. Set ZDASH_REPO=/path/to/zdash."
}

ZDASH_REPO="$(resolve_repo)"
INSTALLER="${LEGACY_INSTALLER:-$ZDASH_REPO/install-zdash-prod-legacy.sh}"

materialize_legacy_installer() {
  if [ -f "$INSTALLER" ]; then
    return
  fi

  command -v git >/dev/null 2>&1 ||
    die "Legacy installer is absent and git is unavailable."

  if ! git -C "$ZDASH_REPO" cat-file -e \
      "${BASE_INSTALLER_REF}:install-zdash-prod.sh" 2>/dev/null; then
    die "Cannot recover the original installer from git ref $BASE_INSTALLER_REF."
  fi

  INSTALLER="$ZDASH_REPO/install-zdash-prod-legacy.sh"

  # Keep the recovered implementation beside the wrapper so the legacy script
  # resolves the current repository as its application source. Exclude the
  # generated file locally so it does not dirty an otherwise clean checkout.
  if [ -d "$ZDASH_REPO/.git" ]; then
    mkdir -p "$ZDASH_REPO/.git/info"
    touch "$ZDASH_REPO/.git/info/exclude"
    if ! grep -qxF "/install-zdash-prod-legacy.sh" "$ZDASH_REPO/.git/info/exclude"; then
      printf '%s\n' "/install-zdash-prod-legacy.sh" >>"$ZDASH_REPO/.git/info/exclude"
    fi
  fi

  git -C "$ZDASH_REPO" show \
    "${BASE_INSTALLER_REF}:install-zdash-prod.sh" >"$INSTALLER"
  chmod 700 "$INSTALLER"
  log "Materialized the original installer from git ref $BASE_INSTALLER_REF"
}

read_env_value() {
  local key="$1"
  local line=""

  [ -f "$ENV_FILE" ] || return 0
  line="$(grep -m1 -E "^${key}=" "$ENV_FILE" 2>/dev/null || true)"
  [ -n "$line" ] || return 0
  printf '%s' "${line#*=}"
}

load_runtime_identity() {
  local value=""

  # Explicit environment values always win. Existing runtime values are used only
  # when a value was not supplied by the operator.
  for key in \
    POSTGRES_DB \
    POSTGRES_USER \
    POSTGRES_PASSWORD \
    REDIS_PASSWORD \
    JWT_SECRET_KEY \
    BOOTSTRAP_ADMIN_USERNAME \
    BOOTSTRAP_ADMIN_PASSWORD \
    ZDASH_DOMAIN \
    ZDASH_PUBLIC_URL
  do
    if [ -z "${!key:-}" ]; then
      value="$(read_env_value "$key")"
      if [ -n "$value" ]; then
        printf -v "$key" '%s' "$value"
        export "$key"
      fi
    fi
  done

  POSTGRES_DB="${POSTGRES_DB:-zdash}"
  POSTGRES_USER="${POSTGRES_USER:-zdash}"
  BOOTSTRAP_ADMIN_USERNAME="${BOOTSTRAP_ADMIN_USERNAME:-admin}"
  ZDASH_DOMAIN="${ZDASH_DOMAIN:-zdash.zeaz.dev}"
  ZDASH_PUBLIC_URL="${ZDASH_PUBLIC_URL:-https://$ZDASH_DOMAIN}"

  export POSTGRES_DB POSTGRES_USER
  export BOOTSTRAP_ADMIN_USERNAME ZDASH_DOMAIN ZDASH_PUBLIC_URL
}

validate_runtime_secrets() {
  if [ -f "$ENV_FILE" ]; then
    [ -n "${POSTGRES_PASSWORD:-}" ] ||
      die "POSTGRES_PASSWORD is missing from $ENV_FILE."
    [ -n "${REDIS_PASSWORD:-}" ] ||
      die "REDIS_PASSWORD is missing from $ENV_FILE."
    [ -n "${JWT_SECRET_KEY:-}" ] ||
      die "JWT_SECRET_KEY is missing from $ENV_FILE."
    [ -n "${BOOTSTRAP_ADMIN_PASSWORD:-}" ] ||
      die "BOOTSTRAP_ADMIN_PASSWORD is missing from $ENV_FILE."
  fi
}

backup_runtime_files() {
  local stamp backup_dir
  stamp="$(date +%Y%m%d-%H%M%S)"
  backup_dir="$INSTALL_ROOT/backups/pre-recovery-$stamp"
  mkdir -p "$backup_dir"

  [ ! -f "$ENV_FILE" ] || cp -a "$ENV_FILE" "$backup_dir/.env.production"
  [ ! -f "$COMPOSE_FILE" ] || cp -a "$COMPOSE_FILE" "$backup_dir/docker-compose.yml"

  chmod 700 "$backup_dir"
  [ ! -f "$backup_dir/.env.production" ] || chmod 600 "$backup_dir/.env.production"
  log "Runtime backup saved: $backup_dir"
}

dc() {
  [ -f "$ENV_FILE" ] || die "Runtime env not found: $ENV_FILE"
  [ -f "$COMPOSE_FILE" ] || die "Compose file not found: $COMPOSE_FILE"
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
}

container_exists() {
  docker inspect "$1" >/dev/null 2>&1
}

container_health() {
  docker inspect \
    --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' \
    "$1" 2>/dev/null || true
}

repair_postgres_role_password() {
  [ -n "${POSTGRES_PASSWORD:-}" ] || {
    warn "Cannot repair PostgreSQL: POSTGRES_PASSWORD is empty."
    return 1
  }

  container_exists zdash-postgres || {
    warn "PostgreSQL container does not exist yet."
    return 1
  }

  log "Aligning the PostgreSQL role password with the protected runtime environment"

  # The official PostgreSQL image permits local administrative access from inside
  # the container. psql variable quoting prevents the password from being emitted
  # into logs or interpolated as SQL syntax.
  if ! docker exec -i zdash-postgres \
      psql \
      --username "$POSTGRES_USER" \
      --dbname "$POSTGRES_DB" \
      --set ON_ERROR_STOP=1 \
      --set "zdash_password=$POSTGRES_PASSWORD" <<'SQL'
ALTER ROLE CURRENT_USER WITH LOGIN PASSWORD :'zdash_password';
SQL
  then
    warn "Could not update the database role password."
    return 1
  fi

  log "PostgreSQL role password aligned successfully"
}

restart_backend() {
  log "Restarting the backend after credential reconciliation"
  dc up -d --no-deps backend >/dev/null
  docker restart zdash-backend >/dev/null
}

wait_for_backend() {
  local elapsed=0
  local state=""

  log "Waiting for backend health (timeout: ${BACKEND_HEALTH_TIMEOUT}s)"
  while [ "$elapsed" -lt "$BACKEND_HEALTH_TIMEOUT" ]; do
    state="$(container_health zdash-backend)"
    case "$state" in
      healthy)
        log "Backend is healthy"
        return 0
        ;;
      exited|dead)
        warn "Backend entered state: $state"
        return 1
        ;;
    esac
    sleep 5
    elapsed=$((elapsed + 5))
  done

  warn "Backend did not become healthy within ${BACKEND_HEALTH_TIMEOUT}s."
  return 1
}

collect_diagnostics() {
  local stamp out
  stamp="$(date +%Y%m%d-%H%M%S)"
  mkdir -p "$DIAG_DIR"
  out="$DIAG_DIR/zdash-recovery-$stamp.log"

  {
    echo "zDash production recovery diagnostics"
    echo "timestamp=$(date -Is)"
    echo "repo=$ZDASH_REPO"
    echo "runtime=$RUNTIME_DIR"
    echo
    echo "== docker compose ps =="
    dc ps || true
    echo
    echo "== backend inspect =="
    docker inspect \
      --format 'status={{.State.Status}} health={{if .State.Health}}{{.State.Health.Status}}{{end}} exit={{.State.ExitCode}} error={{.State.Error}}' \
      zdash-backend 2>&1 || true
    echo
    echo "== backend logs =="
    dc logs --no-color --tail=300 backend 2>&1 || true
    echo
    echo "== postgres logs =="
    dc logs --no-color --tail=120 postgres 2>&1 || true
    echo
    echo "== redis logs =="
    dc logs --no-color --tail=120 redis 2>&1 || true
  } >"$out"

  chmod 600 "$out"
  warn "Diagnostics written to: $out"
}

repair_current_stack() {
  load_runtime_identity
  validate_runtime_secrets
  backup_runtime_files

  dc up -d postgres redis >/dev/null
  repair_postgres_role_password
  restart_backend

  if ! wait_for_backend; then
    collect_diagnostics
    return 1
  fi

  dc up -d frontend nginx
  dc ps
}

run_safe_install() {
  materialize_legacy_installer
  [ -f "$INSTALLER" ] || die "Legacy installer not found: $INSTALLER"
  [ -x "$INSTALLER" ] || chmod +x "$INSTALLER"

  load_runtime_identity

  if [ -f "$ENV_FILE" ]; then
    validate_runtime_secrets
    backup_runtime_files

    # Reconcile the current role before running the installer. This repairs the
    # common state where a prior run rewrote .env.production but PostgreSQL kept
    # the password stored in its persistent volume.
    if container_exists zdash-postgres; then
      repair_postgres_role_password || true
    fi

    log "Reusing existing production secrets; no persistent secret will be rotated"
  else
    log "No existing runtime environment found; the installer will generate first-run secrets"
  fi

  log "Running the original production installer safely"
  set +e
  (
    cd "$ZDASH_REPO"
    "$INSTALLER"
  )
  install_rc=$?
  set -e

  # Reload values because a first installation creates the environment file.
  load_runtime_identity

  if [ "$install_rc" -ne 0 ] || [ "$(container_health zdash-backend)" != "healthy" ]; then
    warn "Installer returned rc=$install_rc or backend is not healthy; starting automatic recovery"
    validate_runtime_secrets
    dc up -d postgres redis >/dev/null || true
    repair_postgres_role_password || true
    restart_backend || true

    if ! wait_for_backend; then
      collect_diagnostics
      die "Backend recovery failed. Review the diagnostic log shown above."
    fi

    dc up -d frontend nginx
  fi

  log "Final service status"
  dc ps

  log "Backend HTTP health"
  docker exec -i zdash-backend python - <<'PY'
import urllib.request
print(urllib.request.urlopen("http://127.0.0.1:8005/health", timeout=10).read().decode())
PY

  printf '\nCompleted successfully.\n'
  printf 'URL: %s\n' "$ZDASH_PUBLIC_URL"
  printf 'Runtime environment preserved: %s\n' "$ENV_FILE"
}

main() {
  mkdir -p "$DIAG_DIR"

  if [ "$REPAIR_ONLY" = "true" ]; then
    repair_current_stack
  else
    run_safe_install
  fi
}

main "$@"
