#!/usr/bin/env bash
set -Eeuo pipefail
PHASE="${1:-}"
if [ -z "$PHASE" ]; then
  echo "Usage: bash .codex/run-phase.sh 24"
  exit 1
fi
PROMPT="docs/prompt/phase${PHASE}.prompt"
if [ ! -f "$PROMPT" ]; then
  echo "Prompt not found: $PROMPT"
  find docs/prompt -maxdepth 1 -type f -name "*.prompt" | sort || true
  exit 1
fi
cat "$PROMPT"
