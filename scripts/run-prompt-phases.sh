#!/usr/bin/env bash
set -Eeuo pipefail

# ============================================================
# zDash Codex Phase-by-Phase Runner
# Repo: cvsz/zdash
# Prompt dir: docs/prompt
#
# Examples:
#   ./scripts/run-prompt-phases.sh
#   FROM=1 TO=32 ./scripts/run-prompt-phases.sh
#   FROM=2 TO=32 ./scripts/run-prompt-phases.sh
#   FROM=10 TO=10 ./scripts/run-prompt-phases.sh
#   AUTOCOMMIT=1 ./scripts/run-prompt-phases.sh
#   VALIDATE_CMD="npm test" ./scripts/run-prompt-phases.sh
# ============================================================

PROMPT_DIR="${PROMPT_DIR:-docs/prompt}"
FROM="${FROM:-1}"
TO="${TO:-32}"
AUTOCOMMIT="${AUTOCOMMIT:-0}"
CONTINUE_ON_ERROR="${CONTINUE_ON_ERROR:-0}"
CODEX_SANDBOX="${CODEX_SANDBOX:-workspace-write}"
CODEX_ARGS="${CODEX_ARGS:-}"
VALIDATE_CMD="${VALIDATE_CMD:-}"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_DIR=".codex/runs/$RUN_ID"
mkdir -p "$LOG_DIR"

if ! command -v codex >/dev/null 2>&1; then
  echo "ERROR: codex CLI not found."
  echo "Install/login Codex first, then re-run."
  exit 1
fi

if [ ! -d "$PROMPT_DIR" ]; then
  echo "ERROR: prompt directory not found: $PROMPT_DIR"
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "WARNING: repo has existing uncommitted changes."
  echo "Continuing, but phase diffs may mix with current work."
fi

run_validate() {
  local phase="$1"

  if [ -n "$VALIDATE_CMD" ]; then
    echo "VALIDATE: $VALIDATE_CMD"
    bash -lc "$VALIDATE_CMD" 2>&1 | tee "$LOG_DIR/${phase}.validate.log"
    return "${PIPESTATUS[0]}"
  fi

  if [ -f package.json ]; then
    node -e '
      const p=require("./package.json");
      if (p.scripts?.test) process.exit(0);
      process.exit(1);
    ' >/dev/null 2>&1 && {
      echo "VALIDATE: npm test"
      npm test 2>&1 | tee "$LOG_DIR/${phase}.validate.log"
      return "${PIPESTATUS[0]}"
    }
  fi

  if [ -f pyproject.toml ] || [ -d tests ]; then
    if command -v pytest >/dev/null 2>&1; then
      echo "VALIDATE: pytest"
      pytest 2>&1 | tee "$LOG_DIR/${phase}.validate.log"
      return "${PIPESTATUS[0]}"
    fi
  fi

  echo "VALIDATE: skipped, no VALIDATE_CMD/test runner detected." | tee "$LOG_DIR/${phase}.validate.log"
  return 0
}

run_phase() {
  local phase="$1"
  local file="$2"

  if [ ! -f "$file" ]; then
    echo "SKIP: missing $file" | tee -a "$LOG_DIR/summary.log"
    return 0
  fi

  echo ""
  echo "============================================================"
  echo "RUN PHASE: $phase"
  echo "PROMPT:    $file"
  echo "LOG DIR:   $LOG_DIR"
  echo "============================================================"

  local tmp_prompt
  tmp_prompt="$(mktemp)"

  cat > "$tmp_prompt" <<HEADER
You are Codex running a controlled phase-by-phase implementation for repository cvsz/zdash.

Current phase: $phase
Prompt file: $file

Execution rules:
1. Inspect the repository before editing.
2. Implement this phase completely; do not only summarize.
3. Preserve existing behavior unless this phase explicitly requires a migration.
4. Do not hardcode secrets, tokens, private keys, or credentials.
5. Add/update tests where practical.
6. Update docs/config/deployment files when behavior changes.
7. Run the most relevant validation commands available in this repo.
8. At the end, report:
   - changed files
   - implemented features
   - validation commands run
   - remaining risks/gaps
   - next phase recommendation

Now execute the phase prompt below.

============================================================
HEADER

  cat "$file" >> "$tmp_prompt"

  set +e
  codex exec \
    --cd "$ROOT" \
    --sandbox "$CODEX_SANDBOX" \
    -o "$LOG_DIR/${phase}.final.md" \
    - $CODEX_ARGS < "$tmp_prompt" \
    2>&1 | tee "$LOG_DIR/${phase}.log"
  local codex_status="${PIPESTATUS[0]}"
  set -e

  rm -f "$tmp_prompt"

  if [ "$codex_status" -ne 0 ]; then
    echo "FAILED: $phase codex_status=$codex_status" | tee -a "$LOG_DIR/summary.log"
    if [ "$CONTINUE_ON_ERROR" != "1" ]; then
      exit "$codex_status"
    fi
    return 0
  fi

  set +e
  run_validate "$phase"
  local validate_status="$?"
  set -e

  if [ "$validate_status" -ne 0 ]; then
    echo "FAILED: $phase validate_status=$validate_status" | tee -a "$LOG_DIR/summary.log"
    if [ "$CONTINUE_ON_ERROR" != "1" ]; then
      exit "$validate_status"
    fi
  fi

  git status --short > "$LOG_DIR/${phase}.git-status.txt"
  git diff --stat > "$LOG_DIR/${phase}.diffstat.txt"

  if [ "$AUTOCOMMIT" = "1" ]; then
    if ! git diff --quiet || ! git diff --cached --quiet; then
      git add -A
      git commit -m "phase: complete ${phase}" || true
    else
      echo "AUTOCOMMIT: no changes for $phase"
    fi
  fi

  echo "DONE: $phase codex_status=$codex_status validate_status=$validate_status" | tee -a "$LOG_DIR/summary.log"
}

for n in $(seq 1 32); do
  if [ "$n" -lt "$FROM" ] || [ "$n" -gt "$TO" ]; then
    continue
  fi

  phase="$(printf 'phase%02d' "$n")"
  file="$(printf '%s/phase%02d.prompt' "$PROMPT_DIR" "$n")"
  run_phase "$phase" "$file"
done

echo ""
echo "ALL REQUESTED PHASES COMPLETE."
echo "Logs:    $LOG_DIR"
echo "Summary: $LOG_DIR/summary.log"
