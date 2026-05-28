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

echo "Validating Docker..."
cd ..
docker build -f infra/docker/backend.Dockerfile .
docker build -f infra/docker/frontend.Dockerfile .
docker build -f infra/docker/nginx.Dockerfile .
docker compose config
docker compose -f docker-compose.prod.yml config

echo "Committing Phase 09.5..."
ECC_SKIP_PRECOMMIT=1 git add .
ECC_SKIP_PRECOMMIT=1 git commit -m "phase09.5: add enterprise cloud deployment templates" --no-gpg-sign

echo "Validation and commit successful!"
