---
name: zdash
description: zDash repository development patterns, safety invariants, phase workflow, and validation commands for cvsz/zdash.
---

# zDash Development Skill

Use this skill when working in `cvsz/zdash`.

zDash is a safety-first AI operations dashboard and agent runtime for staged automation, trading simulation, governance, observability, and enterprise control workflows.

## Core Rules

- Read `AGENTS.md` before changing code.
- Read the requested `docs/prompt/phaseXX.prompt` before phase work.
- Implement only the requested phase or task.
- Preserve the current green CI baseline.
- Do not rewrite the repository from scratch.
- Do not commit secrets or private data.
- Use mocks, adapters, and dependency injection for external providers.
- Keep live trading, real broker execution, real IoT actions, real social posting, real infrastructure mutation, raw shell relay, and destructive automation disabled by default.

## Runtime Defaults

- Backend default port: `8004`
- Backend health endpoint: `http://localhost:8004/health`
- Frontend dev endpoint: `http://localhost:5173`
- Support domain: `https://zdash.zeaz.dev`
- Cloudflare operator repo: `CVSz/zeaz-platform`

## Backend Commands

```bash
cd backend
pytest
```

If dependencies are missing:

```bash
bash .codex/cloud/repair-backend-deps.sh
```

## Frontend Commands

```bash
cd frontend
npm install --legacy-peer-deps --no-audit --fund=false
npm test
npm run build
```

Important:

- Use `npm test`, not `npm test -- --run`.
- `npm test` already runs Vitest with `--run`.
- Production build uses `frontend/tsconfig.build.json` and must not compile `src/tests/**`.

## Docker Commands

```bash
docker build -f infra/docker/backend.Dockerfile .
docker build -f infra/docker/frontend.Dockerfile .
```

## Phase Workflow

Phase prompts live in `docs/prompt/`.

Run one phase at a time unless explicitly asked for a batch:

```bash
FROM=1 TO=1 ./scripts/run-prompt-phases.sh
FROM=2 TO=2 ./scripts/run-prompt-phases.sh
```

Validation override:

```bash
VALIDATE_CMD='if [ -d backend ]; then cd backend && pytest && cd ..; fi; if [ -d frontend ]; then cd frontend && npm install --legacy-peer-deps --no-audit --fund=false && npm test && npm run build && cd ..; fi' FROM=1 TO=1 ./scripts/run-prompt-phases.sh
```

## Event Rules

- `Event.message` must be a human-readable string.
- Put structured event details in `Event.payload`.

## Agent Rules

- Any class extending `BaseAgent` must call `BaseAgent.__init__()`.
- Any class extending `BaseAgent` must implement required abstract methods.

## CI Troubleshooting

If Vitest fails with duplicate `--run`, call only:

```bash
npm test
```

If TypeScript build fails on test globals, ensure build uses:

```bash
tsc -p tsconfig.build.json
```

If backend tests fail on missing packages, update both:

```text
backend/pyproject.toml
backend/requirements.txt
```

Then run:

```bash
bash .codex/cloud/repair-backend-deps.sh
cd backend && pytest
```
