# zDash · Safety-First AI Operations Dashboard

**Short description:** zDash is a safety-first AI operations dashboard and agent runtime for staged automation, trading simulation, governance, observability, and enterprise control workflows.

Repository: `cvsz/zdash`

Public/support domain:

```text
https://zdash.zeaz.dev
```

Cloudflare operator source of truth:

```text
https://github.com/CVSz/zeaz-platform
```

Use this repository for application code, local configuration defaults, backend/frontend implementation, tests, and documentation. Use `CVSz/zeaz-platform` for Cloudflare DNS, Pages/Tunnel routing, Access, WAF, API Shield, edge health checks, and production support-domain rollout.

---

## Current Runtime Summary

| Area | Current default |
|---|---|
| Backend | FastAPI on `0.0.0.0:8005` |
| Frontend | React/Vite on `0.0.0.0:5173` |
| Node/npm | Use `nvm`, Node 20 LTS. Do **not** install Ubuntu `apt npm`. |
| Python | Python 3.11+ / 3.12 tested in Ubuntu VM |
| Trading | Simulation/dry-run only by default |
| IoT | Dry-run + confirmation-gated by default |
| Social posting | Dry-run + approval-gated by default |
| Strategy promotion | Disabled by default |
| Main dashboard | Team roster is now rendered on `/` |
| Team route | `/team` remains available |

Common local endpoints:

```text
Backend health:  http://localhost:8005/health
Backend API:     http://localhost:8005/api
Frontend dev:    http://localhost:5173
VM browser:      http://192.168.74.128:5173
```

---

## Safety First

zDash includes trading, automation, IoT, social posting, update, support, fleet, marketplace, and security-operations concepts. These capabilities are intentionally **dry-run, mock, read-only, or approval-gated by default**.

Never enable by default:

- live trading
- real broker order execution
- real IoT power actions
- real social posting
- secret export
- real infrastructure mutation
- real update apply or rollback execution
- raw shell relay
- unreviewed plugin execution
- destructive automation

Never bypass:

- Victor Hale / Guardian risk checks
- drawdown guard checks
- kill switch / halt flag checks
- content approval checks
- RBAC
- tenant isolation
- audit logging
- policy/certification/attestation gates when present
- backup/readiness checks before real mutation

Trading-related modules are for **simulation, dry-run, and system testing only**. Nothing in this repository is financial advice.

---

## Canonical Agent Roster

Stable backend/API IDs must remain unchanged for routing, event correlation, tests, URLs, and compatibility. Use the new display names in dashboards, docs, reports, and metadata.

| Tier | Stable ID | Display name | Title | Legacy alias |
|---|---|---|---|---|
| Legendary | `ceo` | Alexander Prime | CEO · Visionary Leader | CEO |
| Epic | `janie` | Sophia Lane | Coordinator · Manager | Janie |
| Epic | `guardian` | Victor Hale | Risk Manager | Guardian |
| Epic | `editor` | Elena Voss | Content Specialist | Editor |
| Epic | `social` | Maya Quinn | Social Media Specialist | Social |
| Epic | `graphic` | Julian Reed | Design Specialist | Graphic |
| Epic | `trading` / strategy modules | Damien Cross | Trading Specialist | Trading Specialist |
| Rare | `joe` | Nathan Cole | Analyst · Developer | Joe |
| Rare | `friday` | Isla Grant | Scheduler · Automation | Friday |

Canonical roster prompt:

```text
docs/prompt/agent-roster.prompt
```

Recommended wording:

```text
Alexander Prime delegates execution to Sophia Lane. Sophia Lane coordinates Victor Hale, Isla Grant, Nathan Cole, Elena Voss, Julian Reed, Maya Quinn, and Damien Cross.
```

---

## Repository Layout

```text
.
├── AGENTS.md                         # Canonical repo-level coding-agent guide
├── README.md                         # Project overview and developer entrypoint
├── LICENSE                           # MIT License
├── SECURITY.md                       # Security reporting and safety policy
├── CONTRIBUTING.md                   # Contribution workflow
├── COMMUNITY.md                      # Community and support guidance
├── CODE-OF-CONDUCT.md                # Community behavior expectations
├── .env.example                      # Safe environment template
├── .github/workflows/                # CI, frontend CI, security CI
├── .codex/cloud/                     # Codex Cloud setup suite
├── config/ecc/                       # ECC / Codex CLI integration references
├── docs/prompt/                      # Phase prompt files and canonical roster prompt
├── scripts/                          # Setup, run, and phase runner scripts
├── backend/                          # FastAPI backend
├── frontend/                         # React/Vite frontend
└── infra/docker/                     # Backend/frontend Dockerfiles
```

Important files:

```text
AGENTS.md
SECURITY.md
CONTRIBUTING.md
COMMUNITY.md
CODE-OF-CONDUCT.md
.codex/cloud/general-custom-instructions.md
.codex/cloud/setup.sh
.codex/cloud/maintenance.sh
scripts/run-prompt-phases.sh
backend/pyproject.toml
frontend/package.json
frontend/.npmrc
frontend/tsconfig.build.json
infra/docker/backend.Dockerfile
infra/docker/frontend.Dockerfile
```

---

## Ubuntu / VMware Full-Stack Setup

### Important Node rule

Do **not** run:

```bash
sudo apt install nodejs npm
```

Ubuntu `npm` can conflict with NodeSource `nodejs`. Use `nvm` instead.

### Recommended local installer

Use the local `install-zdash-fullstack.sh` helper generated during repair. It should:

- avoid `apt npm`
- install Node through `nvm`
- install backend tools such as `ruff`, `pytest`, `httpx`, and `uvicorn`
- avoid `autopep8 --aggressive`
- recover known formatter-corrupted files safely
- remove stray untracked `package.json` / `package-lock.json` files outside `frontend/`
- write helper scripts: `run-backend.sh`, `run-frontend.sh`, `healthcheck-zdash.sh`, `fix-gpg-signing.sh`, `commit-zdash-safe.sh`

Typical run:

```bash
cd ~
bash install-zdash-fullstack.sh
```

Fast mode without frontend tests:

```bash
RUN_FRONTEND_TESTS=false bash install-zdash-fullstack.sh
```

Force recovery of known formatter-damaged files:

```bash
RECOVER_CORRUPT_FILES=true bash install-zdash-fullstack.sh
```

Skip recovery:

```bash
RECOVER_CORRUPT_FILES=false bash install-zdash-fullstack.sh
```

---

## Manual Backend Setup

```bash
cd ~/zdash/backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e '.[dev]' || python -m pip install -e .
python -m pip install --upgrade ruff pytest pytest-cov httpx uvicorn
```

Backend validation:

```bash
cd ~/zdash/backend
source .venv/bin/activate
python -m ruff check app tests --fix
python -m ruff check app tests
python -B -m pytest -q
```

Do not use `autopep8 --aggressive` on the backend. It can corrupt compact generated files by moving `return` statements and local variables outside of functions.

---

## Manual Frontend Setup

```bash
source ~/.nvm/nvm.sh
nvm install 20
nvm use 20

cd ~/zdash/frontend
npm install --legacy-peer-deps --no-audit --fund=false
npm test
npm run build
```

`frontend/.npmrc` intentionally sets `legacy-peer-deps=true` while the current Vite/plugin dependency graph is being stabilized.

`npm test` already runs Vitest in one-shot mode through `vitest --run --passWithNoTests`. Do **not** run `npm test -- --run`; that passes `--run` twice and fails on newer Vitest.

---

## Run the App

Backend:

```bash
cd ~/zdash/backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

Frontend:

```bash
source ~/.nvm/nvm.sh
nvm use 20
cd ~/zdash/frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

Open:

```text
http://192.168.74.128:5173
```

Backend health:

```bash
curl http://127.0.0.1:8005/health
curl http://192.168.74.128:8005/health
```

Check listening ports:

```bash
ss -lntp | grep -E ':5173|:8005'
```

Expected listeners:

```text
0.0.0.0:5173
0.0.0.0:8005
```

If Windows cannot reach the VM browser URL, use an SSH tunnel:

```powershell
ssh -L 5173:127.0.0.1:5173 -L 8005:127.0.0.1:8005 zeazdev@192.168.74.128
```

Then open:

```text
http://localhost:5173
```

---

## Dashboard Notes

### Phase 07 Overview

Phase 07 delivers the full React/Vite operations dashboard with all module pages wired to backend APIs and mock-safe fallback behavior.

### Dashboard Architecture

- app shell: `Sidebar` + `Topbar` + `PageHeader` under `frontend/src/components/layout/`
- page modules: `frontend/src/pages/*` for Dashboard, Team Roster, Trading, Risk, Scheduler, Backtests, Content, IoT, Org Map, Logs, and Settings
- API layer: `frontend/src/api/client.ts` with canonical backend envelope parsing
- mock fallback: `frontend/src/api/mockData.ts` + endpoint-level fallbacks in `frontend/src/api/endpoints.ts`
- safety-first UI state: badges, banners, and confirmation dialogs across trading, risk, scheduler, content, and IoT actions

### Canonical Roster Reference

Use `docs/prompt/agent-roster.prompt` as the source of truth for stable IDs and display names:

- Alexander Prime (`ceo`)
- Sophia Lane (`janie`)
- Victor Hale (`guardian`)
- Isla Grant (`friday`)
- Nathan Cole (`joe`)
- Elena Voss (`editor`)
- Julian Reed (`graphic`)
- Maya Quinn (`social`)
- Damien Cross (`trading`)

### Frontend Environment Variables

Set values in `frontend/.env.example`:

```env
VITE_APP_NAME=zDash
VITE_API_BASE_URL=http://localhost:8005
VITE_WS_BASE_URL=
VITE_ENABLE_MOCK_FALLBACK=true
VITE_POLL_INTERVAL_MS=5000
VITE_DEFAULT_THEME=dark
VITE_SHOW_SAFETY_BANNERS=true
```

`VITE_WS_BASE_URL` is optional. If unset, collaboration and realtime WebSocket clients derive `ws://`/`wss://` from `VITE_API_BASE_URL`.

### Run Backend + Frontend Together

Backend:

```bash
cd ~/zdash/backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

Frontend:

```bash
source ~/.nvm/nvm.sh
nvm use 20
cd ~/zdash/frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

### Mock Fallback Behavior

- if backend fetch fails or times out, the frontend API client can serve safe mock data
- mock fallback keeps dashboard pages renderable offline
- UI surfaces show simulated mode banners and dry-run status

### Page List

- `/` Dashboard
- `/team` Team Roster
- `/xau` XAU Dashboard
- `/risk` Risk Panel
- `/scheduler` Scheduler
- `/backtests` Backtests
- `/content` Content Pipeline
- `/iot` IoT Control
- `/org` Org Map
- `/logs` Session Logs
- `/settings` Settings

### Safety Banners and Guardrails

- trading actions default to dry-run controls and explicit risk approval checks
- risk panel highlights halt/kill-switch and drawdown state
- content publishing remains approval-gated and social dry-run by default
- IoT power-cycle requires confirmation and typed confirmation in real mode
- app-level safety banner is controlled via `VITE_SHOW_SAFETY_BANNERS`

### Frontend Validation Commands

```bash
source ~/.nvm/nvm.sh
nvm use 20
cd ~/zdash/frontend
npm install --legacy-peer-deps --no-audit --fund=false
npm test
npm run build
```

### Backend Validation Commands

```bash
cd ~/zdash/backend
source .venv/bin/activate
python -m ruff check app tests
python -B -m pytest -q
```

---

## Phase Prompt System

Phase prompts live under:

```text
docs/prompt/
```

Canonical phase set:

```text
phase01.prompt
phase02.prompt
phase03.prompt
phase04.prompt
phase05.prompt
phase06.prompt
phase07.prompt
phase08.prompt
phase09.prompt
phase10.prompt
phase11.prompt
phase12.prompt
phase13.prompt
phase14.prompt
phase15.prompt
phase16.prompt
phase17.prompt
phase18.prompt
phase19.prompt
phase20.prompt
phase21.prompt
phase22.prompt
phase23.prompt
phase24.prompt
phase25.prompt
phase26.prompt
phase27.prompt
phase28.prompt
phase29.prompt
phase30.prompt
phase31.prompt
phase32.prompt
agent-roster.prompt
```

Run one phase at a time unless explicitly doing a batch:

```bash
FROM=1 TO=1 ./scripts/run-prompt-phases.sh
FROM=2 TO=2 ./scripts/run-prompt-phases.sh
FROM=1 TO=32 ./scripts/run-prompt-phases.sh
```

Recommended batch chunks:

```bash
FROM=1 TO=5 ./scripts/run-prompt-phases.sh
FROM=6 TO=10 ./scripts/run-prompt-phases.sh
FROM=11 TO=15 ./scripts/run-prompt-phases.sh
FROM=16 TO=20 ./scripts/run-prompt-phases.sh
FROM=21 TO=25 ./scripts/run-prompt-phases.sh
FROM=26 TO=32 ./scripts/run-prompt-phases.sh
```

---

## Blueprint Roadmap

| Phase | Area | Summary |
|---:|---|---|
| 01 | Foundation | Sophia Lane server/runtime, Alexander Prime/Sophia Lane agents, mock AI fallback, event bus, health APIs. |
| 02 | Trading Core | Damien Cross trading core: XAU scanner, MT5 adapter shell, Funnel Filter 21/10/3, signal validation, dry-run execution. |
| 03 | Risk System | Victor Hale risk layer, drawdown guard, kill switch, halt flag, risk-gated execution. |
| 04 | Automation | Isla Grant scheduler, IoT adapter shell, Windows service/NSSM run guidance. |
| 05 | Backtesting | Nathan Cole strategy lab, backtest engine, optimizer, simulation-only strategy promotion. |
| 06 | Content Pipeline | Elena Voss, Julian Reed, and Maya Quinn content/design/social workflow with approval-gated publishing. |
| 07 | Dashboard | React/Vite dashboard integration for agents, trading, logs, scheduler, backtests, and roster. |
| 08–20 | Expansion | Extended SaaS, governance, operations, plugin, compliance, and hardening phases. |
| 21 | Federation | Federated governance, trust network, verifiable AI OS concepts. |
| 22 | Advanced Ops | Extended governance/enterprise controls according to phase prompt. |
| 23 | Pre-Endgame | Final bridge prompt before customer/cloud/endgame phases. |
| 24 | Certification | Autonomous certification, auditor portal, enterprise deployment packs. |
| 25 | Customer Cloud | Customer installer, managed update channel, enterprise SLA automation. |
| 26 | Fleet/Relay | Managed fleet control, customer agent relay, remote diagnostics. |
| 27 | AI Ops | AI Ops autopilot, self-healing dry-runs, SRE copilot, RCA packs. |
| 28 | Data Plane | Enterprise data plane, knowledge graph, governed RAG. |
| 29 | Marketplace | Partner marketplace federation, revenue ops, app-store readiness. |
| 30 | Endgame | Final release, board pack, acquisition/IPO dossier, launch command center. |
| 31 | Sovereign Cloud | Air-gapped enterprise, offline update mirror, sovereign deployment patterns. |
| 32 | Security Ops | SOC dashboard, threat detection, Zero Trust hardening. |

---

## Phase 05 Backtesting

Phase 05 introduces the **Strategy Lab** and **Nathan Cole agent** for deterministic strategy research in simulation mode:

- `joe` stable ID, display name `Nathan Cole`
- deterministic mock OHLCV dataset provider for `XAUUSD/M5`
- safe CSV dataset loading from `backend/data/backtests/` only
- strategy interface + variants:
  - `ob_aggressive`
  - `ob_conservative`
  - `trend_follow`
- backtest engine with non-overlapping-trade simulation
- metrics engine
- parameter-sweep optimizer with hard combination cap
- strategy promotion gate with risk thresholds
- scheduler `backtest` job integration through `BacktestService`

Safety notes:

- Research/simulation/paper-trading validation only
- No financial advice
- Backtest results are not guaranteed future performance
- Live trading remains disabled by default
- `DRY_RUN=true` remains default
- Strategy promotion remains disabled by default (`ALLOW_STRATEGY_PROMOTION=false`)
- Promotion does not enable live trading and does not disable Victor Hale / Guardian risk controls

API examples use port **8005**:

```bash
curl http://localhost:8005/api/backtesting/strategies
```

```bash
curl -X POST http://localhost:8005/api/backtesting/run \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "ob_aggressive",
    "symbol": "XAUUSD",
    "timeframe": "M5",
    "dataset": "mock",
    "initial_balance": 10000,
    "risk_per_trade_percent": 1,
    "parameters": {}
  }'
```

```bash
curl -X POST http://localhost:8005/api/backtesting/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "ob_aggressive",
    "symbol": "XAUUSD",
    "timeframe": "M5",
    "dataset": "mock",
    "initial_balance": 10000,
    "parameter_grid": {
      "lookback": [8, 12, 16],
      "risk_reward": [1.5, 2.0, 2.5],
      "confidence_threshold": [0.5, 0.55, 0.6],
      "atr_multiplier": [1.0, 1.2, 1.5]
    },
    "sort_metric": "profit_factor",
    "max_combinations": 50
  }'
```

```bash
curl -X POST http://localhost:8005/api/backtesting/results/RESULT_ID/promotion-check
curl http://localhost:8005/api/backtesting/results/RESULT_ID/report
```

---

## Phase 06 Content Pipeline

Phase 06 adds the approval-gated content workflow coordinated by:

- `editor` (`Elena Voss`) for draft/edit/policy checks
- `graphic` (`Julian Reed`) for graphic prompts and mock image generation
- `social` (`Maya Quinn`) for scheduling/approval/dry-run publishing
- `friday` (`Isla Grant`) scheduler job `content_pipeline` integration via `ContentPipeline.run_full_pipeline()`

Pipeline flow:

1. create draft
2. edit content
3. policy check
4. graphic prompt
5. mock graphic generation
6. stop and wait for manual approval/publish

Safety controls:

- `SOCIAL_DRY_RUN=true` by default
- `SOCIAL_APPROVAL_REQUIRED=true` by default
- `SOCIAL_AUTO_POST_ENABLED=false` by default
- policy failure blocks approval/publish
- mock adapters are used by default (no real social/image API calls)
- trading/strategy/backtesting posts must include educational/simulation disclaimers

API examples (port **8005**):

```bash
curl http://localhost:8005/api/content/status
```

```bash
curl -X POST http://localhost:8005/api/content/create \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "zDash Strategy Lab backtesting summary",
    "content_type": "educational",
    "brand": "zDash",
    "language": "en",
    "tone": "professional",
    "platforms": ["x", "linkedin"],
    "context": {
      "disclaimer": "Backtest results are not guaranteed future performance."
    }
  }'
```

```bash
curl -X POST http://localhost:8005/api/content/generate-graphic \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "CONTENT_ID",
    "style": "clean futuristic dashboard visual",
    "aspect_ratio": "16:9",
    "instructions": "Use zDash product style"
  }'
```

```bash
curl -X POST http://localhost:8005/api/content/approve \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "CONTENT_ID",
    "approved_by": "operator",
    "notes": "Reviewed and approved"
  }'
```

```bash
curl -X POST http://localhost:8005/api/content/post \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "CONTENT_ID",
    "platforms": ["x", "linkedin"],
    "confirmation": false
  }'
```

```bash
curl -X POST http://localhost:8005/api/content/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "zDash weekly system update",
    "content_type": "announcement",
    "brand": "zDash",
    "language": "en",
    "tone": "professional",
    "platforms": ["x", "linkedin"],
    "context": {
      "source": "manual",
      "approval_required": true,
      "dry_run": true
    }
  }'
```

---

## Phase 08 (8.0-8.5)

Phase 08 delivers the production-hardening layer while preserving safety defaults.

Sub-phase summary:

- 8.0: planning and integration baseline for persistence, auth, and operations hardening
- 8.1: SQLAlchemy foundation, session lifecycle, Alembic migrations, repository compatibility layer
- 8.2: JWT auth + RBAC backend controls
- 8.3: audit logging, observability metrics, admin safety-check APIs
- 8.4: frontend login/session handling, protected routes, role-aware navigation, admin dashboard
- 8.5: Docker/NGINX/prod-compose, backup/restore scripts, CI hardening, documentation updates

Production architecture:

- NGINX edge (`infra/docker/nginx.Dockerfile`) serving frontend and reverse-proxying `/api/*` to backend on `8005`
- FastAPI backend (`infra/docker/backend.Dockerfile`) on `8005` with healthcheck and non-root runtime
- Frontend static build (`infra/docker/frontend.Dockerfile`) served via NGINX
- PostgreSQL persistence with init script (`infra/postgres/init.sql`)
- Redis for queue/cache/runtime support
- Prometheus scraping `/api/metrics`

Database persistence:

- local/dev default: SQLite (`sqlite:///./zdash.db`)
- production mode: PostgreSQL `DATABASE_URL` required and safety-gated
- migrations managed via Alembic from backend startup/migration flow

Auth and RBAC:

- JWT-based auth endpoints under `/api/auth/*`
- role-aware admin APIs under `/api/admin/*`
- frontend protected routes and admin-only navigation

Audit and metrics:

- admin audit logs endpoint: `/api/admin/audit-logs`
- safety-check endpoint: `/api/admin/safety-check`
- Prometheus-compatible metrics endpoint: `/api/metrics`

API examples (always port `8005`, never `8000`):

```bash
curl -X POST http://localhost:8005/api/auth/bootstrap-admin
curl -X POST http://localhost:8005/api/auth/login
curl http://localhost:8005/api/admin/safety-check -H "Authorization: Bearer TOKEN"
```

### Docker Local Dev

```bash
docker compose -f docker-compose.yml up --build
```

Default local services:

- backend: `8005`
- frontend: `5173`
- postgres: `5432`
- redis: `6379`

### Docker Production Deploy

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Production-like services:

- nginx: `80`
- backend: internal `8005`
- frontend: internal `80`
- postgres: `5432`
- redis: `6379`
- prometheus: `9090`

### Backup and Restore

Create backup:

```bash
POSTGRES_HOST=localhost POSTGRES_PORT=5432 POSTGRES_USER=zdash POSTGRES_DB=zdash \
POSTGRES_PASSWORD=change-me RETENTION_DAYS=7 ./infra/scripts/backup-postgres.sh
```

Restore backup (requires explicit confirmation):

```bash
RESTORE_CONFIRM=yes POSTGRES_HOST=localhost POSTGRES_PORT=5432 POSTGRES_USER=zdash \
POSTGRES_DB=zdash POSTGRES_PASSWORD=change-me ./infra/scripts/restore-postgres.sh ./backups/FILE.sql.gz
```

### CI Workflow

`.github/workflows/ci.yml` runs:

- `backend-tests` (ruff + pytest)
- `frontend-tests` (vitest + build)
- `docker-build` (backend/frontend/nginx images + compose config validation)

### Safety Checklist

- keep `DRY_RUN=true` unless all production gates are explicitly approved
- keep `LIVE_TRADING_ACK=false` unless formal go-live authorization exists
- keep `PRODUCTION_SAFETY_LOCK=true` for fail-closed behavior
- keep `RISK_GUARDIAN_ENABLED=true`, `MT5_ENABLED=false` by default
- keep content and IoT in dry-run/approval-required modes by default
- never expose secrets/tokens/JWT keys in logs, metrics, or frontend bundles

### Default Credential and Secret Rotation Warning

- `JWT_SECRET_KEY`, `BOOTSTRAP_ADMIN_PASSWORD`, and `DEFAULT_ADMIN_PASSWORD` defaults are for local/dev only
- rotate JWT/admin secrets before any production deployment
- set `AUTH_ENABLED=true` in production and keep `AUTH_ALLOW_BOOTSTRAP_IN_PRODUCTION=false` after initial secure bootstrap
- disable or rotate default admin credentials immediately after first secure admin creation

### Validation Commands

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

Docker:

```bash
docker build -f infra/docker/backend.Dockerfile .
docker build -f infra/docker/frontend.Dockerfile .
docker compose config
```

---

## Safe Commit / GPG Notes

If signed commit fails with:

```text
Couldn't load public key: No such file or directory
```

reset Git signing to GPG/OpenPGP:

```bash
export GPG_TTY=$(tty)
git config --global --unset gpg.format || true
git config --global gpg.program gpg
git config --global commit.gpgsign true
gpg --list-secret-keys --keyid-format=long
```

Set the key ID shown after `sec .../KEY_ID`:

```bash
git config --global user.signingkey KEY_ID
echo test | gpg --clearsign
```

Commit:

```bash
git add backend frontend README.md .gitignore
git commit -S -m "fix: update zDash"
git push
```

Emergency unsigned commit:

```bash
git commit --no-gpg-sign -m "fix: update zDash"
git push
```

Avoid committing local helper scripts unless intentionally adding them to the repo. Prefer storing generated helpers under:

```text
~/.local/bin/zdash-tools/
```

---

## Environment Variables

Start from:

```bash
cp .env.example .env
```

Safe defaults:

```env
BACKEND_PORT=8005
CLOUDFLARE_HOSTNAME=zdash.zeaz.dev
CLOUDFLARE_OPERATOR_REPO=CVSz/zeaz-platform
DRY_RUN=true
LIVE_TRADING_ACK=false
RISK_GUARDIAN_ENABLED=true
MT5_ENABLED=false
SOCIAL_DRY_RUN=true
SOCIAL_APPROVAL_REQUIRED=true
SOCIAL_AUTO_POST_ENABLED=false
CONTENT_PIPELINE_ENABLED=true
IMAGE_GENERATION_PROVIDER=mock
IOT_DRY_RUN=true
IOT_REQUIRE_CONFIRMATION=true
ALLOW_STRATEGY_PROMOTION=false
UPDATE_DRY_RUN=true
SUPPORT_BUNDLE_INCLUDE_SECRETS=false
DEPLOYMENT_PACK_INCLUDE_SECRETS=false
```

Do not commit `.env` or real provider secrets.

---

## External Provider Policy

Use mocks, adapters, and dependency injection for:

- Claude / OpenAI
- MT5 / broker integrations
- Tapo / IoT integrations
- social media APIs
- image generation APIs
- Stripe
- Cloudflare
- HeyGen
- GitHub
- Slack
- email / SMTP
- cloud providers

Tests must not require real credentials or network access.

Provider adapters must fail safely when:

- dependency is not installed
- credentials are missing
- provider is disabled
- `DRY_RUN=true`
- approval is missing

---

## Development Rules

1. Inspect the repo before editing.
2. Implement only the requested phase/task.
3. Preserve existing behavior.
4. Add safe shims for missing earlier modules.
5. Keep tests passing.
6. Update docs and examples when behavior changes.
7. Never commit secrets.
8. Prefer small, reviewable commits.
9. Report validation commands and results.
10. Document known limitations and next handoff.

---

## Current Known Notes

- `README.md` is the project overview; `AGENTS.md` is the detailed agent policy.
- Codex Cloud custom instructions are intentionally compact to preserve context window.
- `docs/prompt/` is the source of truth for phase-specific work.
- `docs/prompt/agent-roster.prompt` is the source of truth for display agent names.
- Some blueprint phases may be prompt-only until implemented by Codex/agents.
- The existing app should remain safe in mock/dry-run mode even when optional providers are missing.
- Frontend tests and frontend production builds intentionally use separate TypeScript config paths.
- Keep port examples on `8005`, not `8000`.

---

## License

This project is licensed under the MIT License. See `LICENSE`.

## Realtime Operations (Phase 7.7)

- WebSocket endpoint: `GET /api/realtime/ws` (compat: `/api/realtime/ws/events`).
- REST endpoints:
  - `GET /api/realtime/status`
  - `GET /api/realtime/events?limit=100`
  - `POST /api/realtime/mock-event`
- Event categories: `system`, `trading`, `risk`, `scheduler`, `content`, `iot`, `admin`, `audit`.
- Polling fallback remains available through existing API fetch cycles if websocket is unavailable.
- Offline-safe UI behavior: dashboard and notification/event timeline continue to render even when disconnected.
- Mock stream can be enabled via `ENABLE_MOCK_REALTIME=true` and is automatically suppressed during pytest unless explicitly enabled.

## Realtime Layer
- WebSocket endpoint: `/api/realtime/ws` (JSON events only).
- Notification center surfaces severity-tagged realtime events.
- Frontend falls back to simulated realtime mode when socket unavailable.
- System Health includes realtime diagnostics (status, last event, fallback state).
- Safety defaults preserved: dry-run/mock-safe, no secret/token exposure.

## Collaboration
- Workspace collaboration endpoints are dry-run safe and federation remains mock-only.

## Phase 09 Enterprise Cloud Scale

Phase 09 delivers the enterprise scale foundation, ensuring multi-tenant capabilities, cloud infrastructure, and robust background worker processing.

- **Tenancy & Organizations**: The backend and frontend are now tenant-aware. Organizations (`/api/organizations`) and Workspaces (`/api/workspaces`) provide a solid RBAC boundary. The frontend automatically injects `X-ZDash-Tenant` and `X-ZDash-Workspace` headers.
- **Worker Queues**: Background tasks are processed using Celery/Redis (`/api/workers`). Safe retry and dry-run execution are maintained by default.
- **Cloud Infrastructure (`infra/`)**: Docker Compose now natively supports Postgres and Redis. Terraform and Kubernetes YAMLs are available for cloud deployment.
- **Cloudflare Automation**: Cloudflare deployment automation is explicitly delegated to `cvsz/zeaz-platform` rather than operating in `cvsz/zdash`.
- **Safe Runbooks**: Release and rollback scripts ensure that changes are handled safely and consistently.
