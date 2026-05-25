# Codex Cloud · General Custom Instructions

Paste this into Codex Cloud General Custom Instructions.

```text
You are working in repository:

cvsz/zdash

Project:

⬡ zDash · FULL SYSTEM BLUEPRINT v2.0

Primary objective:
Implement each requested phase safely, incrementally, and with production-grade code quality.

Repository rules:

1. Always inspect the repository before coding.
2. Do not rebuild existing modules from scratch.
3. Do not remove existing behavior.
4. If an expected previous phase module is missing, create a minimal compatibility shim instead of breaking the build.
5. Prefer small, reviewable commits.
6. Keep backend and frontend tests passing.
7. Update README, docs, tests, and .env.example when adding features.
8. Never commit secrets.
9. Never expose secrets in frontend code, logs, docs, support bundles, deployment packs, or generated artifacts.
10. Never enable live trading, real IoT power actions, or real social posting by default.
11. Never bypass Guardian risk checks.
12. Never bypass content approval checks.
13. Never bypass RBAC.
14. Never bypass tenant isolation.
15. Never bypass audit logging.
16. All external, remote, cloud, installer, update, support, and automation actions must default to dry-run, read-only, mock mode, or approval-gated mode.

Tech stack assumptions:

Backend:
- Python
- FastAPI
- Pydantic
- SQLAlchemy / SQLite / PostgreSQL where present
- pytest

Frontend:
- React
- Vite
- TypeScript
- Tailwind
- Vitest / React Testing Library

Default verification commands:

Backend:
cd backend && pytest

Frontend:
cd frontend && npm test -- --run && npm run build

If a command fails because dependencies are missing, repair the dependency setup first, then rerun the checks.

Implementation format for every phase:

1. Repository inspection summary
2. Folder tree changes
3. New backend files
4. New frontend files
5. Patched existing files
6. Tests
7. .env.example updates
8. README/docs updates
9. API examples
10. Run/test instructions
11. Safety checklist
12. Known limitations
13. Next phase handoff notes

Prompt files:

- Phase prompts live under docs/prompt/
- Short phase prompt files use lowercase names:
  docs/prompt/phase21.prompt
  docs/prompt/phase22.prompt
  docs/prompt/phase23.prompt
  ...
  docs/prompt/phase32.prompt

Recommended execution order for the integrated prompt set:

phase21.prompt → phase22.prompt → phase23.prompt → phase24.prompt → phase25.prompt → phase26.prompt → phase27.prompt → phase28.prompt → phase29.prompt → phase30.prompt → phase31.prompt → phase32.prompt

Current Codex Cloud helper files live under:

.codex/cloud/
```
