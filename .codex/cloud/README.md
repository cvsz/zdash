# zDash Codex Cloud Setup Suite

Repository: `cvsz/zdash`

This folder contains the Codex Cloud setup/maintenance suite for zDash.
It is designed for safe phase execution with current project constraints:

- current baseline: Phase 01-10 plus Phase 7.10 collaboration/federation foundation
- backend on port `8005`
- frontend dev on port `5173`
- Node `20` via `nvm`
- dry-run/safety defaults preserved
- no secrets in repo
- no `autopep8 --aggressive`
- no Ubuntu `apt npm`
- Cloudflare operator work belongs in `cvsz/zeaz-platform`

## Files

- `general-custom-instructions.md` - compact text for Codex Cloud General Custom Instructions
- `setup.sh` - one-time environment setup script
- `maintenance.sh` - periodic validation + report script
- `repair-backend-deps.sh` - backend dependency repair/sanity helper
- `phase-runner.md` - prompt templates for one-phase and multi-phase runs
- `env.safe.example` - non-secret safety-focused env defaults
- `AGENTS.template.md` - optional bootstrap template for repo agent instructions

## Primary workflow

1. Paste `general-custom-instructions.md` into Codex Cloud General Custom Instructions.
2. Paste `setup.sh` into Codex Cloud Setup Script.
3. Paste `maintenance.sh` into Codex Cloud Maintenance Script.
4. Run one requested phase or codex-run prompt at a time unless batch execution is explicitly requested.
5. Use targeted commits only; avoid `git add .` if unrelated files exist.

## Setup command

```bash
bash .codex/cloud/setup.sh
```

## Maintenance command

```bash
bash .codex/cloud/maintenance.sh
```

## Backend dependency repair

```bash
bash .codex/cloud/repair-backend-deps.sh
```

The repair helper ensures runtime/dev dependencies are importable, including `psycopg[binary]` for `postgresql+psycopg://` production URLs.

## Validation standard

Backend:

```bash
cd backend
source .venv/bin/activate
python -m ruff check app tests
python -B -m pytest -q
```

Frontend:

```bash
cd frontend
source ~/.nvm/nvm.sh
nvm use 20
npm install --legacy-peer-deps --no-audit --fund=false
npm test
npm run build
```

Docker validation when Docker/infra surfaces change:

```bash
docker build -f infra/docker/backend.Dockerfile .
docker build -f infra/docker/frontend.Dockerfile .
docker build -f infra/docker/nginx.Dockerfile .
docker compose config
docker compose -f docker-compose.prod.yml config
```

## Phase 10 documentation

Phase 10 commercial packaging docs:

```text
docs/architecture/PHASE_10_SAAS_MONETIZATION.md
docs/architecture/BILLING_MODEL.md
docs/architecture/MARKETPLACE_MODEL.md
docs/architecture/ENTERPRISE_PACKAGING.md
docs/runbooks/BILLING_INCIDENT_RUNBOOK.md
docs/runbooks/SUBSCRIPTION_SUPPORT_RUNBOOK.md
docs/runbooks/MARKETPLACE_REVIEW_RUNBOOK.md
docs/runbooks/ENTERPRISE_CUSTOMER_RUNBOOK.md
```

Phase 10 safety rules:

- mock billing is default in development
- Stripe is disabled by default
- no raw card data is stored
- marketplace plugins run in sandbox mode by default
- marketplace review is required by default
- enterprise exports exclude secrets by default
- secret export requires `CONFIRM_SECRET_EXPORT`
- backend API examples use port `8005`, never `8000`

## Current hardening watchlist

Before starting a new major phase, inspect or fix:

- backend manifests include `psycopg[binary]` if production compose uses `postgresql+psycopg://`
- collaboration WebSocket validates auth when `AUTH_ENABLED=true`
- workspace federation mutation endpoints require auth/RBAC despite mock-only behavior
- frontend collaboration WebSocket URL derives from `VITE_WS_BASE_URL` or `VITE_API_BASE_URL`, not only `window.location.origin`
- latest `main` CI is green after any Phase 7.10 or later merge

## Cloudflare operator handoff

Cloudflare DNS, Pages/Tunnel, Access, WAF, rate limiting, TLS, and edge routing are managed in:

```text
cvsz/zeaz-platform
```

Support domain:

```text
zdash.zeaz.dev
```

Rules for this repo:

- Do not add Cloudflare tokens, account IDs, zone IDs, tunnel tokens, or origin certs.
- Do not move Cloudflare operator automation into `cvsz/zdash`.
- Keep zDash configs origin-ready: `/health`, `/api/*`, frontend static/app routes.
- Document Cloudflare handoff work for `cvsz/zeaz-platform` when needed.

## Safety invariants

Never enable by default:

- live trading
- real broker execution
- real IoT power actions
- real social posting
- real image generation
- secret export or secret embedding

Never bypass:

- risk guardian / kill switch / halt controls
- content approval controls
- RBAC and tenant boundaries
- audit and policy gates

Any external-impacting action must default to dry-run, read-only, mock, simulation, or explicit approval-gated mode.

## Prompt locations

Primary phase prompts:

```text
docs/prompt/phase01.prompt ... docs/prompt/phase32.prompt
```

Codex run prompts used in local workspaces should remain untracked:

```text
docs/prompt/codex-runs/*.prompt
```

Use `phase-runner.md` templates for both formats.
