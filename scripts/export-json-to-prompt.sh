#!/usr/bin/env bash
set -Eeuo pipefail

# ============================================================
# Export JSON files to .prompt files
#
# Default:
#   input  = docs/prompt
#   output = docs/prompt
#
# Usage:
#   ./scripts/export-json-to-prompt.sh
#   ./scripts/export-json-to-prompt.sh ./respond ./prompts
#   ./scripts/export-json-to-prompt.sh ./responses ./prompt_exports
# ============================================================

INPUT_DIR="${1:-./respond}"
OUTPUT_DIR="${2:-./prompts}"

if [[ ! -d "$INPUT_DIR" ]]; then
  echo "ERROR: input directory not found: $INPUT_DIR" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

python3 - "$INPUT_DIR" "$OUTPUT_DIR" <<'PY'
import json
import sys
from pathlib import Path
from typing import Any

input_dir = Path(sys.argv[1]).resolve()
output_dir = Path(sys.argv[2]).resolve()

SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
}

TEXT_KEYS_PRIORITY = [
    "prompt",
    "master_prompt",
    "system_prompt",
    "user_prompt",
    "instruction",
    "instructions",
    "response",
    "respond",
    "answer",
    "content",
    "message",
    "text",
    "output",
    "result",
    "completion",
]


def is_skipped(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def stringify(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, (int, float, bool)):
        return str(value)

    if isinstance(value, list):
        parts = []
        for item in value:
            text = extract_text(item)
            if text:
                parts.append(text)
        return "\n\n".join(parts).strip()

    if isinstance(value, dict):
        text = extract_text(value)
        if text:
            return text
        return json.dumps(value, ensure_ascii=False, indent=2)

    return str(value).strip()


def extract_openai_like(data: dict) -> str:
    # OpenAI / Claude-style shapes
    parts = []

    choices = data.get("choices")
    if isinstance(choices, list):
        for choice in choices:
            if not isinstance(choice, dict):
                continue

            msg = choice.get("message")
            if isinstance(msg, dict):
                content = msg.get("content")
                if content:
                    parts.append(stringify(content))

            delta = choice.get("delta")
            if isinstance(delta, dict):
                content = delta.get("content")
                if content:
                    parts.append(stringify(content))

            text = choice.get("text")
            if text:
                parts.append(stringify(text))

    content = data.get("content")
    if isinstance(content, list):
        # Claude content blocks: [{"type":"text","text":"..."}]
        for block in content:
            if isinstance(block, dict):
                if block.get("text"):
                    parts.append(stringify(block.get("text")))
                elif block.get("content"):
                    parts.append(stringify(block.get("content")))

    messages = data.get("messages")
    if isinstance(messages, list):
        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get("role", "message")
                content = stringify(msg.get("content", ""))
                if content:
                    parts.append(f"[{role}]\n{content}")

    return "\n\n".join(p for p in parts if p).strip()


def extract_text(data: Any) -> str:
    if isinstance(data, str):
        return data.strip()

    if isinstance(data, list):
        return stringify(data)

    if not isinstance(data, dict):
        return stringify(data)

    # First handle common API response wrappers:
    # {"ok": true, "data": {...}}
    if isinstance(data.get("data"), dict):
        inner = extract_text(data["data"])
        if inner:
            return inner

    # OpenAI / Claude / LLM response shape
    openai_like = extract_openai_like(data)
    if openai_like:
        return openai_like

    # Priority direct keys
    for key in TEXT_KEYS_PRIORITY:
        if key in data:
            text = stringify(data[key])
            if text:
                return text

    # Nested useful keys
    for key in ["payload", "body", "request", "reply", "generated", "metadata"]:
        if isinstance(data.get(key), dict):
            text = extract_text(data[key])
            if text:
                return text

    # Fallback: pretty JSON
    return json.dumps(data, ensure_ascii=False, indent=2)


def unique_output_path(src: Path) -> Path:
    relative = src.relative_to(input_dir)
    target = output_dir / relative
    target = target.with_suffix(".prompt")
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


json_files = [
    p for p in input_dir.rglob("*.json")
    if p.is_file() and not is_skipped(p)
]

if not json_files:
    print(f"No .json files found in: {input_dir}")
    sys.exit(0)

converted = 0
failed = 0

for src in json_files:
    target = unique_output_path(src)

    try:
        raw = src.read_text(encoding="utf-8")
        data = json.loads(raw)
        text = extract_text(data).strip()

        if not text:
            text = raw.strip()

        header = (
            f"# Source: {src.relative_to(input_dir)}\n"
            f"# Exported: JSON → PROMPT\n\n"
        )

        target.write_text(header + text + "\n", encoding="utf-8")
        converted += 1
        print(f"OK: {src} -> {target}")

    except Exception as exc:
        failed += 1
        error_target = target.with_suffix(".error.prompt")
        error_target.write_text(
            f"# Source: {src}\n"
            f"# ERROR: failed to parse JSON\n\n"
            f"{exc}\n",
            encoding="utf-8",
        )
        print(f"FAIL: {src} -> {error_target}: {exc}", file=sys.stderr)

print()
print(f"Done. Converted: {converted}, Failed: {failed}")
print(f"Output directory: {output_dir}")
PY
