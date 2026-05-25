# zDash · Codex Agent Guide

Repository: `cvsz/zdash`

Project: ⬡ zDash · FULL SYSTEM BLUEPRINT v2.0

## Mission

Implement the requested zDash phase safely, incrementally, and completely.

## Required behavior

1. Inspect the repository before coding.
2. Identify existing modules and missing dependencies.
3. Do not rebuild previous phases.
4. Do not remove existing behavior.
5. Create safe compatibility shims for missing earlier modules.
6. Keep backend and frontend tests passing.
7. Add tests for new behavior.
8. Update README, docs, and `.env.example`.
9. Use the standard API response shape.
10. Keep all new data tenant-scoped when tenancy exists.

## Safety invariants

Never:

- commit secrets
- expose secrets in frontend
- log secrets
- export secrets by default
- include secrets in deployment packs or support bundles by default
- enable live trading by default
- enable real IoT power actions by default
- enable real social posting by default
- bypass Guardian risk checks
- bypass content approval
- bypass RBAC
- bypass tenant isolation

All external or customer-impacting workflows must default to:

- dry-run
- read-only
- mock mode
- approval-gated mode

## Required checks

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm test -- --run
npm run build
```

## Prompt files

Use:

```bash
bash .codex/run-phase.sh 24
```

Prompt files live in:

```text
docs/prompt/
```

## Codex Cloud setup files

```text
.codex/cloud/
├── README.md
├── general-custom-instructions.md
├── setup.sh
├── maintenance.sh
├── AGENTS.template.md
├── phase-runner.md
└── env.safe.example
```
