#!/usr/bin/env bash
set -euo pipefail

# Integrate ECC assets into this repo without mutating external state by default.
# Usage:
#   scripts/integrate-ecc.sh [ECC_SOURCE_PATH]
#   scripts/integrate-ecc.sh /home/zeazdev/ECC --apply-global [--update-mcp]

ECC_SOURCE="${1:-/home/zeazdev/ECC}"
shift || true

APPLY_GLOBAL=false
UPDATE_MCP=false

for arg in "$@"; do
  case "$arg" in
    --apply-global) APPLY_GLOBAL=true ;;
    --update-mcp) UPDATE_MCP=true ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 1
      ;;
  esac
done

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT_DIR/config/ecc/codex"

require_file() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    echo "Missing required file: $file" >&2
    exit 1
  fi
}

require_file "$ECC_SOURCE/.codex/config.toml"
require_file "$ECC_SOURCE/.codex/AGENTS.md"
require_file "$ECC_SOURCE/.codex/agents/explorer.toml"
require_file "$ECC_SOURCE/.codex/agents/reviewer.toml"
require_file "$ECC_SOURCE/.codex/agents/docs-researcher.toml"

mkdir -p "$DEST/agents"
cp "$ECC_SOURCE/.codex/config.toml" "$DEST/config.toml"
cp "$ECC_SOURCE/.codex/AGENTS.md" "$DEST/AGENTS.md"
cp "$ECC_SOURCE/.codex/agents/explorer.toml" "$DEST/agents/explorer.toml"
cp "$ECC_SOURCE/.codex/agents/reviewer.toml" "$DEST/agents/reviewer.toml"
cp "$ECC_SOURCE/.codex/agents/docs-researcher.toml" "$DEST/agents/docs-researcher.toml"

# Keep a small local snapshot of available ECC skills for discovery.
if [[ -d "$ECC_SOURCE/.agents/skills" ]]; then
  find "$ECC_SOURCE/.agents/skills" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort > "$ROOT_DIR/config/ecc/skills-index.txt"
fi

echo "Integrated ECC baseline into: $DEST"

# Try project-local .codex sync only if writable in this environment.
if [[ -d "$ROOT_DIR/.codex" && -w "$ROOT_DIR/.codex" ]]; then
  mkdir -p "$ROOT_DIR/.codex/agents"
  cp "$DEST/config.toml" "$ROOT_DIR/.codex/config.toml"
  cp "$DEST/AGENTS.md" "$ROOT_DIR/.codex/AGENTS.md"
  cp "$DEST/agents"/*.toml "$ROOT_DIR/.codex/agents/"
  echo "Synced writable project .codex directory."
else
  echo "Project .codex is not writable here; kept files under config/ecc/codex."
fi

if [[ "$APPLY_GLOBAL" == true ]]; then
  require_file "$ECC_SOURCE/scripts/sync-ecc-to-codex.sh"
  cmd=("$ECC_SOURCE/scripts/sync-ecc-to-codex.sh")
  if [[ "$UPDATE_MCP" == true ]]; then
    cmd+=("--update-mcp")
  fi
  echo "Applying ECC to ~/.codex via: ${cmd[*]}"
  "${cmd[@]}"
fi
