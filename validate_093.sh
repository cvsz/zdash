#!/bin/bash
set -e

echo "Validating Backend..."
cd /home/zeazdev/zdash/backend
source .venv/bin/activate
python -m ruff check app tests
python -B -m pytest -q

echo "Validating Frontend..."
cd ../frontend
source ~/.nvm/nvm.sh
nvm use 20
npm test
npm run build

echo "Validation successful!"
