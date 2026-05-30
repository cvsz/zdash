#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== Git Status ==="
echo ""
echo "--- Short Status ---"
git -C "$ROOT_DIR" status --short
echo ""
echo "--- Working Tree Diff ---"
git -C "$ROOT_DIR" diff --stat
echo ""
echo "--- Staged Diff ---"
git -C "$ROOT_DIR" diff --cached --stat

# Check for risky files
RISKY_PATTERNS=(
  ".env"
  ".env.*"
  "*.pem"
  "*.key"
  "Makefile.bak.*"
  "backend.log"
  "frontend.log"
  ".runtime/"
)

RISKY_FOUND=false
while IFS= read -r line; do
  for pattern in "${RISKY_PATTERNS[@]}"; do
    if [[ "$line" == *"$pattern"* ]]; then
      if ! $RISKY_FOUND; then
        echo ""
        echo "=== Risky Files Detected ==="
        RISKY_FOUND=true
      fi
      echo "  ⚠ $line"
      break
    fi
  done
done < <(git -C "$ROOT_DIR" diff --cached --name-status 2>/dev/null || true)

if $RISKY_FOUND; then
  echo ""
  echo "Review risky files before committing."
fi
