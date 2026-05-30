#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== Pre-Push Validation ==="
echo ""

echo "--- Validate Fast ---"
make -C "$ROOT_DIR" validate-fast || {
  echo "validate-fast failed. Fix issues before pushing."
  exit 1
}

echo ""
echo "--- Safe Status ---"
bash "$ROOT_DIR/scripts/git/safe-status.sh"

echo ""
echo "--- Pushing to origin/main ---"
if git -C "$ROOT_DIR" push origin main 2>&1; then
  echo "Push successful."
else
  PUSH_EXIT=$?
  echo ""
  echo "Push failed (exit code $PUSH_EXIT)."
  echo ""
  echo "If GitHub push protection blocked a secret:"
  echo "  1. Do NOT use the unblock URL for real secrets."
  echo "  2. Rotate/delete any leaked cloud keys immediately."
  echo "  3. Recover:"
  echo "     git fetch origin main"
  echo "     git reset --soft origin/main"
  echo "     # Remove secret from files"
  echo "     bash scripts/git/safe-add.sh"
  echo "     make validate-fast"
  echo "     bash scripts/git/safe-commit.sh \"Remove leaked secret\""
  echo "     bash scripts/git/safe-push.sh"
  echo ""
  echo "For real credential leaks, rotate the key at the provider immediately."
  exit $PUSH_EXIT
fi
