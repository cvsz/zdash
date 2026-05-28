#!/bin/bash
set -e

cd /home/zeazdev/zdash/backend
source .venv/bin/activate
python -m ruff check app tests
python -B -m pytest -q

cd ../frontend
source ~/.nvm/nvm.sh
nvm use 20
npm test
npm run build

cd ..
docker build -f infra/docker/backend.Dockerfile .
docker build -f infra/docker/frontend.Dockerfile .
docker build -f infra/docker/nginx.Dockerfile .
docker compose config > /dev/null
docker compose -f docker-compose.prod.yml config > /dev/null
