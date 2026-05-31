#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(pwd)"
DIR="docs/prompt"

shopt -s nullglob

for old in "$DIR"/phase[0-9][0-9]*.prompt; do
  base="$(basename "$old")"

  [[ "$base" =~ ^phase([0-9]{2})(.*)\.prompt$ ]] || continue

  num="${BASH_REMATCH[1]}"
  suffix="${BASH_REMATCH[2]}"

  # remove repeated -exec
  while [[ "$suffix" == -exec* ]]; do
    suffix="${suffix#-exec}"
  done

  new="$DIR/phase${num}-exec${suffix}.prompt"

  [[ "$old" == "$new" ]] && continue

  echo "$old -> $new"

  if git ls-files --error-unmatch "$old" >/dev/null 2>&1; then
    git mv "$old" "$new"
  else
    mv "$old" "$new"
  fi
done
