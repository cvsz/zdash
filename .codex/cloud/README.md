# zDash Codex Cloud Setup Suite

Repository: `cvsz/zdash`

This folder contains the Codex Cloud setup/maintenance suite for zDash.
It is designed for safe phase execution with current project constraints:

- backend on port `8005`
- Node `20` via `nvm`
- dry-run/safety defaults preserved
- no secrets in repo

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
4. Run one requested phase at a time unless batch execution is explicitly requested.

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

Optional Docker validation (when Docker surfaces change):

```bash
docker build -f infra/docker/backend.Dockerfile .
docker build -f infra/docker/frontend.Dockerfile .
docker compose config
```

## Safety invariants

Never enable by default:

- live trading
- real broker execution
- real IoT power actions
- real social posting
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

Codex run prompts used in this repo:

```text
docs/prompt/codex-runs/*.prompt
```

Use `phase-runner.md` templates for both formats.
