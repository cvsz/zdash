#!/usr/bin/env bash
set -Eeuo pipefail

# Safe default: show the intended policy without modifying the repository.
mode="--dry-run"
if (( $# > 0 )); then
  mode="$1"
fi
if [[ "$mode" != "--apply" && "$mode" != "--dry-run" ]]; then
  echo "Usage: bash scripts/github/configure-main-protection.sh [--dry-run|--apply]" >&2
  exit 2
fi

payload="$(mktemp)"
trap 'rm -f -- "$payload"' EXIT
cat >"$payload" <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "backend-tests",
      "frontend-tests",
      "docker-build",
      "postgres-dr",
      "backend-lint",
      "frontend-lint",
      "security",
      "dependency-review",
      "e2e",
      "analyze-python",
      "analyze-javascript-typescript"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 0
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
JSON

if [[ "$mode" == "--dry-run" ]]; then
  echo "DRY RUN: intended protection for cvsz/zdash main (no API writes)."
  cat "$payload"
  exit 0
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "BLOCKED: install and authenticate GitHub CLI with repository admin permission." >&2
  exit 1
fi
admin="$(gh api repos/cvsz/zdash --jq '.permissions.admin' 2>/dev/null || true)"
if [[ "$admin" != "true" ]]; then
  echo "BLOCKED: the authenticated GitHub account lacks repository administration permission." >&2
  exit 1
fi

# Run only after the new postgres-dr CI job has succeeded on the protected branch.
gh api --method PUT repos/cvsz/zdash/branches/main/protection \
  -H "Accept: application/vnd.github+json" --input "$payload" >/dev/null

if [[ "$(gh api repos/cvsz/zdash/branches/main --jq '.protected')" != "true" ]]; then
  echo "FAIL: main branch protection could not be verified." >&2
  exit 1
fi
echo "PASS: main protected; PRs, required checks, no force-push/deletion, and admin enforcement configured."
