# zDash · FULL SYSTEM BLUEPRINT v2.0

`cvsz/zdash` is a staged AI operations dashboard and agent-runtime project. The repository is organized around a phase-by-phase blueprint from **Phase 01** through **Phase 32**, with prompt files under `docs/prompt/` and Codex Cloud tooling under `.codex/cloud/`.

The current repository may contain a partial implementation of the full blueprint. Treat the phase prompts as the implementation roadmap, not as proof that every module already exists. Agents and contributors should inspect the repository before coding, implement one phase at a time, preserve existing behavior, and keep all safety defaults locked.

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

- Guardian risk checks
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

## Repository Layout

```text
.
├── AGENTS.md                         # Canonical repo-level coding-agent guide
├── README.md                         # Project overview and developer entrypoint
├── .env.example                      # Safe environment template
├── .github/workflows/                # CI, frontend CI, security CI
├── .codex/cloud/                     # Codex Cloud setup suite
├── config/ecc/                       # ECC / Codex CLI integration references
├── docs/prompt/                      # Phase prompt files phase01.prompt → phase32.prompt
├── scripts/                          # Setup, run, and phase runner scripts
├── backend/                          # FastAPI backend
├── frontend/                         # React/Vite frontend
└── infra/docker/                     # Backend/frontend Dockerfiles
```

Important files:

```text
AGENTS.md
.codex/cloud/README.md
.codex/cloud/general-custom-instructions.md
.codex/cloud/setup.sh
.codex/cloud/maintenance.sh
.codex/cloud/repair-backend-deps.sh
scripts/run-prompt-phases.sh
backend/pyproject.toml
backend/requirements.txt
frontend/package.json
frontend/.npmrc
infra/docker/backend.Dockerfile
infra/docker/frontend.Dockerfile
```

---

## Quickstart

### 1. Clone and enter repo

```bash
git clone https://github.com/cvsz/zdash.git
cd zdash
```

### 2. Run Codex Cloud/local setup helper

```bash
bash .codex/cloud/setup.sh
```

The setup helper repairs backend dependencies, installs frontend dependencies using the current peer-dependency policy, creates helper scripts under `.codex/`, and runs an initial healthcheck.

### 3. Manual backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -e '.[dev]'
pytest
```

Fallback / CI-compatible install:

```bash
cd backend
pip install -r requirements.txt
pytest
```

### 4. Manual frontend setup

```bash
cd frontend
npm install --legacy-peer-deps --no-audit --fund=false
npm test -- --run
npm run build
```

`frontend/.npmrc` intentionally sets `legacy-peer-deps=true` while the current Vite/plugin dependency graph is being stabilized. Do not remove it unless the lockfile and dependency graph are intentionally repaired.

---

## Run the App

Backend:

```bash
cd backend
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm run dev
```

Healthcheck:

```bash
curl http://localhost:8000/health
```

---

## Validation Commands

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm install --legacy-peer-deps --no-audit --fund=false
npm test -- --run
npm run build
```

Full helper:

```bash
bash .codex/healthcheck.sh
```

Codex Cloud maintenance:

```bash
bash .codex/cloud/maintenance.sh
```

---

## Codex Cloud Setup Suite

Codex Cloud files live under:

```text
.codex/cloud/
├── README.md
├── general-custom-instructions.md
├── setup.sh
├── maintenance.sh
├── repair-backend-deps.sh
├── AGENTS.template.md
├── phase-runner.md
└── env.safe.example
```

Use `general-custom-instructions.md` as a compact Codex Cloud UI prompt. Keep detailed repo behavior in `AGENTS.md` to avoid wasting context window.

Recommended Codex flow:

1. Paste `.codex/cloud/general-custom-instructions.md` into Codex Cloud General Custom Instructions.
2. Use `.codex/cloud/setup.sh` as the Setup Script.
3. Use `.codex/cloud/maintenance.sh` as the Maintenance Script.
4. Start tasks phase-by-phase using files under `docs/prompt/`.

---

## Agent Guide

Read `AGENTS.md` before making changes. It defines:

- repo map
- safety invariants
- phase execution policy
- backend/frontend conventions
- CI/Docker rules
- secret handling rules
- external provider mock policy
- ECC / Codex CLI integration notes

Codex Cloud custom instructions should stay short and point to `AGENTS.md` plus the requested phase prompt.

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

Full validation override:

```bash
VALIDATE_CMD='if [ -d backend ]; then cd backend && pytest && cd ..; fi; if [ -d frontend ]; then cd frontend && npm install --legacy-peer-deps --no-audit --fund=false && npm test -- --run && npm run build && cd ..; fi' FROM=1 TO=32 ./scripts/run-prompt-phases.sh
```

---

## Blueprint Roadmap

| Phase | Area | Summary |
|---:|---|---|
| 01 | Foundation | Janie Server, Agent Runtime, CEO/Janie agents, mock AI fallback, event bus, health APIs. |
| 02 | Trading Core | XAU scanner, MT5 adapter shell, Funnel Filter 21/10/3, signal validation, dry-run execution. |
| 03 | Risk System | Guardian agent, drawdown guard, kill switch, halt flag, risk-gated execution. |
| 04 | Automation | Scheduler, IoT adapter shell, Windows service/NSSM run guidance. |
| 05 | Backtesting | Strategy lab, backtest engine, optimization, simulation-only strategy promotion. |
| 06 | Content Pipeline | Editor, Graphic, Social agents, mock image/social adapters, approval-gated publishing. |
| 07 | Dashboard | React/Vite dashboard integration for agents, trading, logs, scheduler, backtests. |
| 08–20 | Expansion | Extended SaaS, governance, operations, plugin, compliance, and system hardening phases. |
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

## Backend

Backend stack:

- Python 3.11+
- FastAPI
- Pydantic v2
- pydantic-settings
- SQLModel / SQLAlchemy where persistence exists
- Alembic where migrations exist
- pytest
- httpx for API tests

Key manifests:

```text
backend/pyproject.toml
backend/requirements.txt
```

Rules:

- Keep `backend/requirements.txt` in sync when adding runtime dependencies.
- Keep tests deterministic and offline.
- Provider integrations must be optional and mock-safe.
- Missing optional providers must not crash the app.
- New APIs should use the standard response shape when possible.

Standard response shape:

```json
{
  "ok": true,
  "data": {},
  "error": null,
  "timestamp": "ISO_DATE"
}
```

Error shape:

```json
{
  "ok": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  },
  "timestamp": "ISO_DATE"
}
```

---

## Frontend

Frontend stack:

- React
- Vite
- TypeScript
- Tailwind where present
- Vitest / React Testing Library where present

Commands:

```bash
cd frontend
npm install --legacy-peer-deps --no-audit --fund=false
npm test -- --run
npm run build
```

Rules:

- Never expose secrets through frontend variables.
- Show dry-run/read-only/approval-required state clearly.
- Disable or hide real mutation actions unless enabled and authorized.
- Use mock fallback when backend modules are missing or disabled.
- Keep TypeScript types aligned with backend API responses.

---

## Docker

Dockerfiles:

```text
infra/docker/backend.Dockerfile
infra/docker/frontend.Dockerfile
```

Build:

```bash
docker build -f infra/docker/backend.Dockerfile .
docker build -f infra/docker/frontend.Dockerfile .
```

Rules:

- Do not bake secrets into images.
- Images must build without real provider credentials.
- Backend image should remain compatible with `backend/requirements.txt`.
- Frontend image should follow current npm peer-dependency policy.

---

## CI

Workflows live under:

```text
.github/workflows/
```

Expected jobs:

- backend tests
- frontend tests/build
- Docker build
- security scan/audit

CI policy:

- backend installs from `backend/pyproject.toml` first, with `backend/requirements.txt` compatibility where needed
- frontend installs with `npm install --legacy-peer-deps --no-audit --fund=false`
- security audits may be non-blocking only when the workflow explicitly marks them non-blocking
- secret scans must remain blocking for real secret patterns

If CI fails, inspect the exact workflow/job log first. Fix source/config root cause. Do not delete tests or weaken safety gates to force green CI.

---

## Environment Variables

Start from:

```bash
cp .env.example .env
```

Safe defaults should keep real actions disabled:

```env
DRY_RUN=true
LIVE_TRADING_ACK=false
RISK_GUARDIAN_ENABLED=true
SOCIAL_DRY_RUN=true
SOCIAL_AUTO_POST_ENABLED=false
IOT_DRY_RUN=true
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

- README is the project overview; `AGENTS.md` is the detailed agent policy.
- Codex Cloud custom instructions are intentionally compact to preserve context window.
- `docs/prompt/` is the source of truth for phase-specific work.
- Some blueprint phases may be prompt-only until implemented by Codex/agents.
- The existing app should remain safe in mock/dry-run mode even when optional providers are missing.

---

## License

No license file is currently declared in this repository. Add a `LICENSE` file before public distribution if required.
