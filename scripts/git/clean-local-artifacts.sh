#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
REMOVED=0

remove_if_exists() {
  local pattern="$1"
  local desc="$2"
  local found=false
  while IFS= read -r f; do
    if [[ -e "$f" ]]; then
      rm -rf "$f"
      echo "  removed: $f"
      found=true
      REMOVED=1
    fi
  done < <(find "$ROOT_DIR" -maxdepth 1 -name "$pattern" 2>/dev/null || true)
  $found && return 0 || true
}

echo "=== Cleaning local artifacts ==="

# Makefile backups
remove_if_exists "Makefile.bak.*" "Makefile backups"

# .bak files (not in .git)
while IFS= read -r f; do
  if [[ -f "$f" ]]; then
    rm -f "$f"
    echo "  removed: $f"
    REMOVED=1
  fi
done < <(find "$ROOT_DIR" -name "*.bak" -not -path "*/.git/*" -not -path "*/node_modules/*" 2>/dev/null || true)

# Generated logs
for logf in backend.log frontend.log; do
  if [[ -f "$ROOT_DIR/$logf" ]]; then
    rm -f "$ROOT_DIR/$logf"
    echo "  removed: $ROOT_DIR/$logf"
    REMOVED=1
  fi
done

# Runtime tmp
if [[ -d "$ROOT_DIR/.runtime/tmp" ]]; then
  rm -rf "$ROOT_DIR/.runtime/tmp"
  echo "  removed: .runtime/tmp/"
  REMOVED=1
fi

if [[ "$REMOVED" -eq 0 ]]; then
  echo "  Nothing to clean."
fi
echo "Done."
