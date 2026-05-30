#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# Run cleanup first
bash "$ROOT_DIR/scripts/git/clean-local-artifacts.sh"

# Patterns that must never be added
UNSAFE_PATTERNS=(
  "^.env$"
  "^.env\\..*"
  "^frontend/.env\\.local$"
  "^Makefile\\.bak\\..*"
  ".*\\.bak$"
  "^backend\\.log$"
  "^frontend\\.log$"
  "^\\.runtime/"
  ".*node_modules/.*"
  "^backend/\\.venv/"
)

reject_unsafe() {
  local path="$1"
  for pattern in "${UNSAFE_PATTERNS[@]}"; do
    if echo "$path" | grep -qE "$pattern"; then
      echo "REJECTED: unsafe path '$path' matches pattern '$pattern'"
      return 0
    fi
  done
  return 1
}

if [[ $# -eq 0 ]]; then
  # No args: add safe project files only
  git -C "$ROOT_DIR" add --all -- ':!.env' ':!.env.*' ':!frontend/.env.local' \
    ':!Makefile.bak.*' ':!*.bak' ':!backend.log' ':!frontend.log' \
    ':!.runtime/' ':!node_modules/' ':!backend/.venv/'
  echo "Added safe project files."
else
  # Explicit paths: check each one
  for arg in "$@"; do
    if reject_unsafe "$arg"; then
      echo "Aborting: unsafe path specified"
      exit 1
    fi
  done
  git -C "$ROOT_DIR" add "$@"
  echo "Added specified paths."
fi

echo ""
echo "Staged files:"
git -C "$ROOT_DIR" diff --cached --stat
