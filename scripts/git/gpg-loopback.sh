#!/usr/bin/env bash
set -Eeuo pipefail

# ============================================================
# GPG loopback helper for signed git commits
# - Reads GPG_PASSPHRASE from .env if present
# - Falls back to hidden prompt if missing
# - Enables allow-loopback-pinentry
# - Preloads gpg-agent cache
# - Runs git commit -S
#
# SECURITY:
# - .env must stay untracked
# - chmod 600 .env
# ============================================================

ACTION="${1:-help}"
shift || true

ENV_FILE="${GPG_ENV_FILE:-.env}"

log() {
  printf '\n\033[1;36m[%s]\033[0m %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

warn() {
  printf '\n\033[1;33m[WARN]\033[0m %s\n' "$*"
}

die() {
  printf '\n\033[1;31m[ERROR]\033[0m %s\n' "$*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing command: $1"
}

ensure_tools() {
  need_cmd git
  need_cmd gpg
  need_cmd gpgconf
  need_cmd python3
}

ensure_env_ignored() {
  if [ -f "$ENV_FILE" ]; then
    chmod 600 "$ENV_FILE" 2>/dev/null || true

    if git rev-parse --show-toplevel >/dev/null 2>&1; then
      if git ls-files --error-unmatch "$ENV_FILE" >/dev/null 2>&1; then
        die "$ENV_FILE is tracked by git. Run: git rm --cached $ENV_FILE && echo '$ENV_FILE' >> .gitignore"
      fi
    fi
  fi
}

read_passphrase_from_env_file() {
  local env_file="$1"

  [ -f "$env_file" ] || return 1

  python3 - "$env_file" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
key = "GPG_PASSPHRASE"

for raw in path.read_text(errors="ignore").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    if not line.startswith(key + "="):
        continue

    value = line.split("=", 1)[1].strip()

    if (
        len(value) >= 2
        and value[0] == value[-1]
        and value[0] in {"'", '"'}
    ):
        value = value[1:-1]

    print(value, end="")
    raise SystemExit(0)

raise SystemExit(1)
PY
}

ensure_loopback_config() {
  mkdir -p "$HOME/.gnupg"
  chmod 700 "$HOME/.gnupg"

  touch "$HOME/.gnupg/gpg-agent.conf"
  touch "$HOME/.gnupg/gpg.conf"

  grep -qxF "allow-loopback-pinentry" "$HOME/.gnupg/gpg-agent.conf" \
    || echo "allow-loopback-pinentry" >> "$HOME/.gnupg/gpg-agent.conf"

  grep -qxF "default-cache-ttl 28800" "$HOME/.gnupg/gpg-agent.conf" \
    || echo "default-cache-ttl 28800" >> "$HOME/.gnupg/gpg-agent.conf"

  grep -qxF "max-cache-ttl 86400" "$HOME/.gnupg/gpg-agent.conf" \
    || echo "max-cache-ttl 86400" >> "$HOME/.gnupg/gpg-agent.conf"

  grep -qxF "use-agent" "$HOME/.gnupg/gpg.conf" \
    || echo "use-agent" >> "$HOME/.gnupg/gpg.conf"

  chmod 600 "$HOME/.gnupg/gpg-agent.conf" "$HOME/.gnupg/gpg.conf"

  gpgconf --kill gpg-agent || true
  gpgconf --launch gpg-agent || true
}

get_key_id() {
  local key_id
  key_id="$(git config --global --get user.signingkey || true)"

  if [ -z "$key_id" ]; then
    key_id="$(gpg --list-secret-keys --keyid-format=long 2>/dev/null \
      | awk '/^sec/ {print $2}' \
      | awk -F/ '{print $2}' \
      | head -n1)"
  fi

  [ -n "$key_id" ] || die "No GPG secret key found. Run: gpg --list-secret-keys --keyid-format=long"
  printf '%s\n' "$key_id"
}

configure_git() {
  local key_id="$1"

  git config --global --unset gpg.format || true
  git config --global gpg.program gpg
  git config --global user.signingkey "$key_id"
  git config --global commit.gpgsign true

  export GPG_TTY
  GPG_TTY="$(tty)"
}

load_passphrase() {
  local passphrase=""

  ensure_env_ignored

  if passphrase="$(read_passphrase_from_env_file "$ENV_FILE" 2>/dev/null)"; then
    if [ -n "$passphrase" ]; then
      printf '%s' "$passphrase"
      return 0
    fi
  fi

  printf "Enter GPG passphrase: " >&2
  IFS= read -rs passphrase
  printf "\n" >&2

  [ -n "$passphrase" ] || die "Empty passphrase."
  printf '%s' "$passphrase"
}

unlock_key() {
  local key_id="$1"
  local passphrase

  export GPG_TTY
  GPG_TTY="$(tty)"

  printf "GPG key: %s\n" "$key_id"

  if [ -f "$ENV_FILE" ]; then
    log "Reading GPG_PASSPHRASE from $ENV_FILE"
  else
    warn "$ENV_FILE not found. Falling back to hidden prompt."
  fi

  passphrase="$(load_passphrase)"

  # Preload gpg-agent cache without printing passphrase.
  printf "gpg-loopback-cache-test" | \
    gpg --batch --yes \
      --pinentry-mode loopback \
      --passphrase-fd 3 \
      --local-user "$key_id" \
      --clearsign >/dev/null 3<<<"$passphrase"

  unset passphrase

  log "GPG agent unlocked."
}

setup_action() {
  ensure_tools
  ensure_loopback_config
  ensure_env_ignored

  local key_id
  key_id="$(get_key_id)"
  configure_git "$key_id"

  log "Configured git GPG signing."
  git config --global --show-origin -l | grep -E 'gpg|signingkey|commit.gpgsign' || true
}

test_action() {
  ensure_tools
  ensure_loopback_config

  local key_id
  key_id="$(get_key_id)"
  configure_git "$key_id"
  unlock_key "$key_id"

  echo "test" | gpg --clearsign >/tmp/gpg-loopback-test.asc
  rm -f /tmp/gpg-loopback-test.asc

  log "GPG signing test passed."
}

commit_action() {
  ensure_tools
  ensure_loopback_config

  local key_id
  key_id="$(get_key_id)"
  configure_git "$key_id"
  unlock_key "$key_id"

  log "Running signed git commit."
  git commit -S "$@"
}

status_action() {
  ensure_tools

  echo "Git signing config:"
  git config --global --show-origin -l | grep -E 'gpg|signingkey|commit.gpgsign' || true

  echo
  echo "Secret keys:"
  gpg --list-secret-keys --keyid-format=long || true

  echo
  echo "Env file:"
  if [ -f "$ENV_FILE" ]; then
    ls -l "$ENV_FILE"
    if git ls-files --error-unmatch "$ENV_FILE" >/dev/null 2>&1; then
      echo "WARNING: $ENV_FILE is tracked by git"
    else
      echo "OK: $ENV_FILE is not tracked by git"
    fi
  else
    echo "$ENV_FILE not found"
  fi

  echo
  echo "GPG agent config:"
  grep -nE 'allow-loopback-pinentry|default-cache-ttl|max-cache-ttl' "$HOME/.gnupg/gpg-agent.conf" 2>/dev/null || true
}

case "$ACTION" in
  setup)
    setup_action
    ;;
  test)
    test_action
    ;;
  commit)
    commit_action "$@"
    ;;
  status)
    status_action
    ;;
  *)
    cat <<USAGE
Usage:
  ./gpg-loopback.sh setup
  ./gpg-loopback.sh test
  ./gpg-loopback.sh status
  ./gpg-loopback.sh commit -m "message"

Env:
  GPG_ENV_FILE=.env

Required .env value:
  Set GPG_PASSPHRASE in your local .env file. Never commit .env.

Recommended:
  cd ~/zdash
  chmod 600 .env
  grep -qxF ".env" .gitignore || echo ".env" >> .gitignore
  ./gpg-loopback.sh setup
  ./gpg-loopback.sh test
  git add <files>
  ./gpg-loopback.sh commit -m "your commit message"
USAGE
    ;;
esac
