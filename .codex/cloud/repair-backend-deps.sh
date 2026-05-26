#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="${CODEX_WORKSPACE_DIR:-$(pwd)}"
cd "$ROOT_DIR"

if [ ! -d "backend" ]; then
  echo "No backend directory found."
  exit 0
fi

cd backend

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel

if [ -f "pyproject.toml" ]; then
  pip install -e ".[dev]" || pip install -e .
elif [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
else
  echo "No backend dependency manifest found. Installing Codex fallback runtime set."
fi

# Defensive fallback for historical phase files that import these packages before
# pyproject metadata was updated. This keeps Codex Cloud setup repairable.
pip install \
  'sqlmodel>=0.0.22' \
  'sqlalchemy>=2.0.30' \
  'alembic>=1.13.2' \
  'python-jose[cryptography]>=3.3.0' \
  'passlib>=1.7.4' \
  'prometheus-client>=0.20.0' \
  'email-validator>=2.2.0' \
  'apscheduler>=3.10.4'

python - <<'PY'
import importlib
mods = [
    'fastapi',
    'pydantic',
    'sqlmodel',
    'sqlalchemy',
    'alembic',
    'jose',
    'passlib',
    'prometheus_client',
    'apscheduler',
]
missing = []
for mod in mods:
    try:
        importlib.import_module(mod)
    except Exception as exc:  # pragma: no cover - setup diagnostic
        missing.append(f'{mod}: {exc}')
if missing:
    print('Missing imports after repair:')
    for item in missing:
        print(' -', item)
    raise SystemExit(1)
print('Backend dependency sanity check passed.')
PY
