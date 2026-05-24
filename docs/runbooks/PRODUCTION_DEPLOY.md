# PRODUCTION_DEPLOY

## Purpose
Deploy zDash with Docker Compose production profile.

## Prerequisites
- Docker + Docker Compose
- Hardened `.env.production`

## Commands
```bash
cp .env.production.example .env.production
# edit secrets and gates

docker compose --profile production up -d --build
```

## Expected output
- Services healthy: postgres, redis, backend, frontend, nginx.

## Failure handling
- Validate compose: `docker compose config`
- Check logs: `docker compose logs backend`

## Rollback steps
- Redeploy previous image tag and run DB rollback if needed.

## Safety notes
- Production blocks default weak secrets.
