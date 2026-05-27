# Codex Cloud · Compact General Custom Instructions

Paste only the block below into **Codex Cloud → General Custom Instructions**.
Keep detailed policy in `AGENTS.md` and phase details in `docs/prompt/`.

```text
Repository: cvsz/zdash
Project: zDash FULL SYSTEM BLUEPRINT v2.0

Read before coding:
1. AGENTS.md
2. .codex/cloud/README.md
3. requested phase prompt only

Execution policy:
- inspect repository before edits
- implement only requested scope
- additive/backward-compatible changes
- do not rebuild previous phases
- do not weaken safety gates
- update tests/docs/env examples when behavior changes

Hard constraints:
- backend port must remain 8005
- never use localhost:8000 in repo changes
- use Node 20 via nvm
- never commit .env or secrets
- never expose secrets to frontend

Safety invariants:
- no live trading by default
- no real IoT power actions by default
- no real social posting by default
- no secret export by default
- no RBAC or tenant isolation bypass
- no Guardian risk bypass

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
docker compose config

Reporting format:
- inspection summary
- files changed
- tests/validation results
- safety checklist
- known limitations
- next handoff notes
```
