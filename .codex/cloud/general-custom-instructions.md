# Codex Cloud · Compact General Custom Instructions

Paste only the block below into **Codex Cloud → General Custom Instructions**.
Keep detailed policy in `AGENTS.md`, project docs in `README.md`, and phase details in `docs/prompt/`.

```text
Repository: cvsz/zdash
Project: zDash FULL SYSTEM BLUEPRINT v2.0
Current baseline: Phase 01-08 plus Phase 7.10 collaboration/federation foundation.
Cloudflare operator repo: cvsz/zeaz-platform
Support domain: zdash.zeaz.dev

Read before coding:
1. AGENTS.md
2. .codex/cloud/README.md
3. docs/prompt/agent-roster.prompt
4. requested phase or codex-run prompt only

Execution policy:
- inspect repository before edits
- implement only requested scope
- additive/backward-compatible changes
- do not rebuild previous phases
- do not weaken safety gates
- update tests/docs/env examples when behavior changes
- use targeted git add; never use git add . when unrelated files exist

Hard constraints:
- backend port must remain 8005
- frontend dev port remains 5173
- never introduce localhost:8000 in repo changes
- use Node 20 via nvm; do not install Ubuntu apt npm
- never run autopep8 --aggressive
- never commit .env or secrets
- never expose secrets to frontend, logs, metrics, or reports
- Cloudflare automation belongs in cvsz/zeaz-platform, not cvsz/zdash

Safety invariants:
- no live trading by default
- no real IoT power actions by default
- no real social posting by default
- no real image generation by default
- no secret export by default
- no RBAC or tenant isolation bypass
- no Guardian risk bypass
- no content approval bypass

Current hardening watchlist:
- keep psycopg[binary] available for postgresql+psycopg:// runtime
- protect collaboration WebSocket auth when AUTH_ENABLED=true
- protect workspace federation mutation endpoints
- derive frontend WS URL from VITE_WS_BASE_URL or VITE_API_BASE_URL

Validation standard:
Backend:
cd backend
source .venv/bin/activate
python -m ruff check app tests
python -B -m pytest -q

Frontend:
cd frontend
source ~/.nvm/nvm.sh
nvm use 20
npm install --legacy-peer-deps --no-audit --fund=false
npm test
npm run build

Docker checks when infra changes:
docker build -f infra/docker/backend.Dockerfile .
docker build -f infra/docker/frontend.Dockerfile .
docker build -f infra/docker/nginx.Dockerfile .
docker compose config
docker compose -f docker-compose.prod.yml config

Reporting format:
- inspection summary
- files changed
- tests/validation results
- Docker/compose validation when relevant
- safety checklist
- known limitations
- next handoff notes
```
