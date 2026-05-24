#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../backend"
../.venv/bin/alembic -c alembic.ini upgrade head
