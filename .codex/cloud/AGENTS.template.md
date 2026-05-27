# zDash · Codex Agent Guide

Repository: `cvsz/zdash`

Project: ⬡ zDash · FULL SYSTEM BLUEPRINT v2.0

## Mission

Implement requested zDash scope safely and incrementally without breaking existing behavior.

## Required behavior

1. Inspect repository before coding.
2. Implement only requested phase/task scope.
3. Keep backward compatibility unless explicitly approved.
4. Do not rebuild earlier phases from scratch.
5. Add minimal shims for missing dependencies when needed.
6. Keep tests and build checks green.
7. Update docs and env examples when behavior changes.
8. Never commit `.env` or secrets.

## Hard constraints

- Backend port must remain `8005`.
- Never introduce `localhost:8000`.
- Use Node `20` via `nvm`.
- Never expose secrets in frontend, logs, metrics, or reports.

## Safety invariants

Never enable by default:

- live trading
- real broker execution
- real IoT power actions
- real social posting
- secret export

Never bypass:

- Guardian risk controls
- content approvals
- RBAC / tenant isolation
- audit logging and policy controls

## Required checks

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
npm test
npm run build
```

Docker (when infra changes):

```bash
docker build -f infra/docker/backend.Dockerfile .
docker build -f infra/docker/frontend.Dockerfile .
docker compose config
```

## Prompt helpers

Print a phase prompt:

```bash
bash .codex/run-phase.sh 08
```

Print a codex-run prompt file:

```bash
bash .codex/run-phase.sh docs/prompt/codex-runs/phase08.5.prompt
```
