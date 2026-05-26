# Codex Cloud · Compact General Custom Instructions

Paste only the block below into **Codex Cloud → General Custom Instructions**.
Keep detailed repo guidance in `AGENTS.md` and phase details in `docs/prompt/phaseXX.prompt` to preserve Codex context window.

```text
Repository: cvsz/zdash
Project: zDash FULL SYSTEM BLUEPRINT v2.0

Read repo guidance before coding:
1. AGENTS.md
2. .codex/cloud/README.md
3. docs/prompt/phaseXX.prompt for the requested phase only

Work policy:
- Inspect the repo before editing.
- Implement only the requested phase/task.
- Do not rebuild previous phases or remove existing behavior.
- Add safe shims for missing earlier modules.
- Update tests/docs/.env.example when behavior changes.
- Use small, reviewable commits.

Safety invariants:
- Never commit or expose secrets.
- Never enable live trading, real broker orders, real IoT power actions, real social posting, secret export, raw shell relay, unreviewed plugins, or destructive automation by default.
- Never bypass Guardian/risk checks, kill switch, content approval, RBAC, tenant isolation, audit logging, certification, attestation, or backup/readiness gates.
- External/customer-impacting actions must default to dry-run, read-only, mock, simulation, or approval-gated mode.
- Any real mutation requires admin permission, typed confirmation, validation/preflight pass, audit event, and rollback/recovery plan where applicable.

Setup/validation:
- Setup: bash .codex/cloud/setup.sh
- Backend repair: bash .codex/cloud/repair-backend-deps.sh
- Frontend install: cd frontend && npm install --legacy-peer-deps --no-audit --fund=false
- Healthcheck: bash .codex/healthcheck.sh
- Backend tests: cd backend && pytest
- Frontend checks: cd frontend && npm test -- --run && npm run build

Prompt execution:
- Phase prompts live in docs/prompt/phase01.prompt through docs/prompt/phase32.prompt.
- Run one phase per task unless the user explicitly requests batch execution.
- Phase runner: FROM=1 TO=1 ./scripts/run-prompt-phases.sh

Final report must include: inspection summary, files changed, tests run, safety checklist, known limitations, and next handoff.
```
