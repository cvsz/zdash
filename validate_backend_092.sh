#!/bin/bash
set -e
cd /home/zeazdev/zdash/backend
source .venv/bin/activate
python -m ruff check app tests
python -B -m pytest -q
echo "Phase 09.2 Backend Validation Complete."
