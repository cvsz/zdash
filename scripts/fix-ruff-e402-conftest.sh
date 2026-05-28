#!/usr/bin/env bash
set -Eeuo pipefail

cd ~/zdash

python3 - <<'PY'
from pathlib import Path

files = [
    Path("backend/app/tests/conftest.py"),
    Path("backend/tests/conftest.py"),
]

for p in files:
    s = p.read_text()

    s = s.replace("from app.db.migrations import run_migrations\nrun_migrations()\n\n", "")
    s = s.replace("from app.db.migrations import run_migrations\n\n", "")

    lines = s.splitlines()
    insert_at = 0

    # Find end of import block.
    paren_depth = 0
    last_import_line = -1

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith("from ") or stripped.startswith("import "):
            last_import_line = i

        paren_depth += line.count("(") - line.count(")")

        if last_import_line >= 0 and paren_depth == 0:
            # Continue while imports/blank lines are still part of top import area.
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if next_line and not next_line.startswith(("from ", "import ")):
                insert_at = i + 1
                break

    if insert_at <= 0:
        raise SystemExit(f"Could not find import block in {p}")

    new_lines = lines[:insert_at]
    new_lines.append("from app.db.migrations import run_migrations")
    new_lines.append("")
    new_lines.append("run_migrations()")
    new_lines.append("")
    new_lines.extend(lines[insert_at:])

    # Collapse excessive blank lines.
    out = "\n".join(new_lines).replace("\n\n\n\n", "\n\n\n")
    p.write_text(out.rstrip() + "\n")
    print(f"patched {p}")
PY

cd backend
source .venv/bin/activate
python -m ruff check app tests --fix
python -m ruff check app tests
python -B -m pytest -q

cd ../frontend
source ~/.nvm/nvm.sh
nvm use 20
npm test
npm run build
