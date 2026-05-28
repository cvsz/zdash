#!/usr/bin/env bash
set -Eeuo pipefail

# ============================================================
# GPG loopback helper for signed git commits
# - Does NOT store passphrase in files
# - Prompts passphrase hidden
# - Enables allow-loopback-pinentry
# - Preloads gpg-agent cache
# - Runs git commit -S
# ============================================================

ACTION="${1:-help}"
shift || true

log() {
  printf '\n\033[1;36m[%s]\033[0m %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
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

unlock_key() {
  local key_id="$1"

  export GPG_TTY
  GPG_TTY="$(tty)"

  printf "GPG key: %s\n" "$key_id"
  printf "Enter GPG passphrase: "
  IFS= read -rs GPG_PASS
  printf "\n"

  [ -n "$GPG_PASS" ] || die "Empty passphrase."

  # Preload gpg-agent cache without writing passphrase to disk.
  printf "gpg-loopback-cache-test" | \
    gpg --batch --yes \
      --pinentry-mode loopback \
      --passphrase-fd 3 \
      --local-user "$key_id" \
      --clearsign >/dev/null 3<<<"$GPG_PASS"

  unset GPG_PASS

  log "GPG agent unlocked for this key."
}

setup_action() {
  ensure_tools
  ensure_loopback_config

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

Recommended:
  cd ~/zdash
  ./gpg-loopback.sh setup
  ./gpg-loopback.sh test
  git add <files>
  ./gpg-loopback.sh commit -m "your commit message"

Notes:
  - Passphrase is prompted hidden.
  - Passphrase is not written to .env or disk.
  - Do not commit this script if you want it local only.
USAGE
    ;;
esac
