# Installation

## Local Install

### Automated Install

```bash
git clone https://github.com/cvsz/zdash.git
cd zdash
make install-local
```

This installs:
- Python virtual environment with backend dependencies
- Frontend npm packages
- Helper scripts for running services

### Manual Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e '.[dev]'
python -m pip install --upgrade ruff pytest pytest-cov httpx uvicorn
```

### Manual Frontend Setup

```bash
source ~/.nvm/nvm.sh
nvm install 20
nvm use 20
cd frontend
npm install --legacy-peer-deps --no-audit --fund=false
```

## Production Install

### Prerequisites

- Ubuntu 22.04+ or Debian 12+
- Docker + Docker Compose
- Root/sudo access

### Install

```bash
sudo ./install-zdash-prod.sh
```

### Configure

```bash
sudo nano /opt/zdash/runtime/.env.production
```

Set required environment variables (see Safety Defaults below).

### Start

```bash
make prod-up
```

## Docker Notes

### Local Development

```bash
docker compose -f docker-compose.yml up --build
```

Services: backend (8005), frontend (5173), postgres (5432), redis (6379)

### Production Deploy

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Services: nginx (80), backend (internal 8005), frontend (internal 80), postgres (5432), redis (6379), prometheus (9090)

## Ubuntu/VMware Notes

- Do **not** install Node.js via `apt`: `sudo apt install nodejs npm`
- Use `nvm` instead: `source ~/.nvm/nvm.sh && nvm install 20`
- If Windows cannot reach the VM, use an SSH tunnel:
  ```bash
  ssh -L 5173:127.0.0.1:5173 -L 8005:127.0.0.1:8005 user@vm-ip
  ```

## Cloudflare/Domain Notes

Public/support domain: `https://zdash.zeaz.dev`

Cloudflare DNS, Pages/Tunnel routing, Access, WAF, API Shield, edge health checks, and production support-domain rollout are managed in:
```text
https://github.com/CVSz/zeaz-platform
```

## Safety Environment Defaults

Start from `.env.example`:

```bash
cp .env.example .env
```

Key safety defaults:

| Variable | Default | Purpose |
|----------|---------|---------|
| `DRY_RUN` | `true` | Prevents real broker execution |
| `LIVE_TRADING_ACK` | `false` | Blocks trade confirmation |
| `MT5_ENABLED` | `false` | Prevents MT5 connection |
| `PRODUCTION_ALLOW_LIVE_ACTIONS` | `false` | Blocks all live mutations |
| `RISK_GUARDIAN_ENABLED` | `true` | Enables risk check enforcement |
| `SOCIAL_DRY_RUN` | `true` | Social posting is dry-run only |
| `IOT_DRY_RUN` | `true` | IoT actions are dry-run only |

## No Secrets in Repo

- Never commit `.env` files or real secrets
- Use `.env.example` with placeholder values
- Rotate JWT and admin secrets before production
- Secret scan: `make safety-scan`
