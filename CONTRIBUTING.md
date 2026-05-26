# Contributing to zDash

Thanks for contributing to zDash.

Short description:

> zDash is a safety-first AI operations dashboard and agent runtime for staged automation, trading simulation, governance, observability, and enterprise control workflows.

Production/support domain:

```text
https://zdash.zeaz.dev
```

Cloudflare operator source of truth:

```text
https://github.com/CVSz/zeaz-platform
```

Use the operator repository for Cloudflare DNS, Pages, Tunnel, Access, WAF, API Shield, and support-domain rollout work.

## Before You Start

Read:

1. `AGENTS.md`
2. `README.md`
3. `.codex/cloud/README.md`
4. the relevant `docs/prompt/phaseXX.prompt`
5. `SECURITY.md`
6. `CODEOFCONDUCT.md`

## Development Policy

1. Inspect the repository before editing.
2. Implement only the requested phase or task.
3. Preserve existing behavior unless the task explicitly requires a migration.
4. Add safe compatibility shims when earlier phase modules are missing.
5. Keep tests deterministic and offline.
6. Update docs, tests, and `.env.example` when behavior changes.
7. Never commit secrets or private data.
8. Prefer small, reviewable commits.

## Safety Defaults

Contributions must preserve safe defaults.

Never enable by default:

- live trading
- real broker order execution
- real IoT power actions
- real social posting
- secret export
- raw shell relay
- real infrastructure mutation
- real update apply or rollback execution
- unreviewed plugin execution
- destructive automation

External or customer-impacting actions must default to dry-run, read-only, mock, simulation, or approval-gated mode.

## Setup

Run the project setup helper:

```bash
bash .codex/cloud/setup.sh
```

Backend dependency repair:

```bash
bash .codex/cloud/repair-backend-deps.sh
```

Frontend install policy:

```bash
cd frontend
npm install --legacy-peer-deps --no-audit --fund=false
```

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -e '.[dev]'
pytest
```

Fallback:

```bash
cd backend
pip install -r requirements.txt
pytest
```

## Frontend

```bash
cd frontend
npm install --legacy-peer-deps --no-audit --fund=false
npm test -- --run
npm run build
```

Do not remove `frontend/.npmrc` unless the dependency graph and lockfile are intentionally repaired.

## Runtime Ports

Default backend port: `8004`

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

Smoke test:

```bash
./scripts/smoke-test.sh
```

## Phase-Based Work

Phase prompts live in:

```text
docs/prompt/
```

Run one phase per task unless explicitly asked for a batch.

Examples:

```bash
FROM=1 TO=1 ./scripts/run-prompt-phases.sh
FROM=2 TO=2 ./scripts/run-prompt-phases.sh
FROM=1 TO=32 ./scripts/run-prompt-phases.sh
```

## Commit and Pull Request Guidance

Use clear commit messages:

```text
feat(area): add capability
fix(area): correct behavior
docs(area): update documentation
chore(area): update tooling/config
test(area): add or update tests
```

A good pull request includes:

- summary of changes
- linked issue or phase prompt
- validation commands and results
- safety checklist
- screenshots for UI changes when useful
- known limitations

## Cloudflare / Support Domain Contributions

`zdash.zeaz.dev` is the supported public domain for zDash.

Use this repository for application code and local config defaults. Use `CVSz/zeaz-platform` for Cloudflare DNS, Pages/Tunnel routing, Access policies, WAF/API Shield, edge health checks, and production support-domain rollout.
