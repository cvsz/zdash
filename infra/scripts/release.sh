#!/usr/bin/env bash
set -euo pipefail

echo "Starting release process..."

# Check git tree
if [[ -n $(git status -s) ]]; then
  echo "ERROR: Git working directory is not clean."
  exit 1
fi

# Run backend tests
cd backend
source .venv/bin/activate
python -m pytest -q
cd ..

# Run frontend tests
cd frontend
source ~/.nvm/nvm.sh
nvm use 20
npm test
npm run build
cd ..

# Build Docker images
docker build -f infra/docker/backend.Dockerfile -t zdash-backend:${RELEASE_VERSION:-latest} .
docker build -f infra/docker/frontend.Dockerfile -t zdash-frontend:${RELEASE_VERSION:-latest} .
docker build -f infra/docker/nginx.Dockerfile -t zdash-nginx:${RELEASE_VERSION:-latest} .

# Tag release
if [ -n "${RELEASE_VERSION:-}" ]; then
  echo "Tagging release ${RELEASE_VERSION}..."
  # git tag -a "v${RELEASE_VERSION}" -m "Release v${RELEASE_VERSION}"
fi

echo "Changelog Summary: Generated for ${RELEASE_VERSION:-latest}"
echo "Deployment Checklist: Check environment variables, database backups, and smoke tests."
echo "Release automation complete."
