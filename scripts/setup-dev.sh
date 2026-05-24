#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ./backend

echo "Development environment ready."
echo "Activate with: source .venv/bin/activate"
