#!/usr/bin/env bash
set -Eeuo pipefail

MODE="${1:---dry-run}"
ROOT="${ROOT:-$(pwd)}"
PROMPT_DIR="${PROMPT_DIR:-$ROOT/docs/prompt}"
MANIFEST="$PROMPT_DIR/phase-rename-manifest.tsv"

[[ "$MODE" == "--dry-run" || "$MODE" == "--apply" ]] || {
  echo "Usage: $0 --dry-run|--apply"
  exit 2
}

: > "$MANIFEST"
printf "old_path\tnew_path\n" >> "$MANIFEST"

shopt -s nullglob

for old in "$PROMPT_DIR"/phase[0-9][0-9]*.prompt; do
  base="$(basename "$old")"

  [[ "$base" =~ ^phase([0-9]{2})(.*)\.prompt$ ]] || continue

  num="${BASH_REMATCH[1]}"
  suffix="${BASH_REMATCH[2]}"

  # avoid phase01-exec-exec.prompt
  suffix="${suffix#-exec}"

  new="$PROMPT_DIR/phase${num}-exec${suffix}.prompt"

  if [[ "$old" == "$new" ]]; then
    echo "KEEP   ${old#$ROOT/}"
  else
    echo "RENAME ${old#$ROOT/} -> ${new#$ROOT/}"
    [[ "$MODE" == "--apply" ]] && git mv "$old" "$new"
  fi

  printf "%s\t%s\n" "${old#$ROOT/}" "${new#$ROOT/}" >> "$MANIFEST"
done

echo
echo "Manifest: ${MANIFEST#$ROOT/}"
