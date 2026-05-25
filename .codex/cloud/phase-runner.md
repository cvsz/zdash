# zDash Codex Cloud Phase Runner

Use these prompts as Codex Cloud tasks.

## Run a specific phase

```text
Read docs/prompt/phase04.prompt.

Implement Phase 04 only.

Requirements:
- Inspect repo first.
- Preserve existing behavior.
- Add safe shims for missing modules.
- Keep all safety defaults locked.
- Add backend/frontend tests.
- Update README and .env.example.
- Run backend and frontend checks.

Return:
1. Inspection summary
2. Files changed
3. Tests run
4. Safety checklist
5. Known limitations
6. Next phase handoff
```

## Generic phase prompt

```text
Read docs/prompt/phase{{PHASE_NUMBER}}.prompt.

Implement Phase {{PHASE_NUMBER}} only.

Do not implement later phases.

Follow all safety invariants:
- no live trading by default
- no real IoT by default
- no real social posting by default
- no secret export by default
- no RBAC bypass
- no tenant isolation bypass
- dry-run/read-only/approval-gated defaults

Run all relevant backend and frontend checks before final response.
```

## Local helper command

After running `.codex/cloud/setup.sh`, the setup script creates:

```bash
bash .codex/run-phase.sh 24
```

This prints the selected prompt file so Codex can use it as task context.

## Recommended phase order

```text
docs/prompt/
├── phase04.prompt
├── phase05.prompt
├── phase06.prompt
├── phase07.prompt
├── phase08.prompt
├── phase09.prompt
├── phase10.prompt
├── phase11.prompt
├── phase12.prompt
├── phase13.prompt
├── phase14.prompt
├── phase15.prompt
├── phase16.prompt
├── phase17.prompt
├── phase18.prompt
├── phase19.prompt
├── phase20.prompt
├── phase21.prompt
├── phase22.prompt
├── phase23.prompt
├── phase24.prompt
├── phase25.prompt
├── phase26.prompt
├── phase27.prompt
├── phase28.prompt
├── phase29.prompt
├── phase30.prompt
├── phase31.prompt
└── phase32.prompt
```

## Verification

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
