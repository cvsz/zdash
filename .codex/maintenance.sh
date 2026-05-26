#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
mkdir -p .codex/reports
REPORT=".codex/reports/maintenance-$(date -u +%Y%m%dT%H%M%SZ).md"
{
  echo "# zDash Maintenance Report"
  echo
  echo "- Date UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "- Branch: $(git branch --show-current 2>/dev/null || true)"
  echo "- Commit: $(git rev-parse --short HEAD 2>/dev/null || true)"
  echo
  echo "## Git status"
  echo '```'
  git status --short || true
  echo '```'
  echo
  echo "## Prompt files"
  echo '```'
  find docs/prompt -maxdepth 1 -type f | sort || true
  echo '```'
} > "$REPORT"
set +e
bash .codex/healthcheck.sh | tee -a "$REPORT"
STATUS="${PIPESTATUS[0]}"
set -e
echo "Maintenance report: $REPORT"
exit "$STATUS"
