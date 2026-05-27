#!/usr/bin/env bash
set -Eeuo pipefail
TARGET="${1:-}"
if [ -z "$TARGET" ]; then
  echo "Usage: bash .codex/run-phase.sh <phase-number-or-prompt-file>"
  echo "Examples:"
  echo "  bash .codex/run-phase.sh 08"
  echo "  bash .codex/run-phase.sh docs/prompt/codex-runs/phase08.5.prompt"
  exit 1
fi

if [ -f "$TARGET" ]; then
  PROMPT="$TARGET"
elif [[ "$TARGET" =~ ^[0-9]+$ ]]; then
  PHASE_PADDED=$(printf "%02d" "$TARGET")
  PROMPT="docs/prompt/phase${PHASE_PADDED}.prompt"
else
  PROMPT="docs/prompt/${TARGET}"
fi

if [ ! -f "$PROMPT" ]; then
  echo "Prompt not found: $PROMPT"
  find docs/prompt -maxdepth 3 -type f -name "*.prompt" | sort || true
  exit 1
fi

cat "$PROMPT"
