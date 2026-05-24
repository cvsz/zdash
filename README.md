# zDash Phase 1 Foundation

Phase 1 provides the Janie Server backend foundation:
- FastAPI server
- Agent runtime (CEO + Janie)
- AI adapter boundary (Mock + Claude-safe fallback)
- In-memory event bus
- Structured JSON logging
- Health, agents, messaging, and logs APIs
- Pytest suite

## Project Structure

```text
zdash/
  README.md
  .env.example
  scripts/
    setup-dev.sh
    setup-dev.ps1
    run-backend.sh
    smoke-test.sh
  backend/
    pyproject.toml
    app/
      __init__.py
      main.py
      core/
        __init__.py
        config.py
        logging.py
        events.py
        responses.py
      agents/
        __init__.py
        base.py
        ceo.py
        janie.py
        registry.py
      ai/
        __init__.py
        base.py
        claude_adapter.py
        mock_adapter.py
      api/
        __init__.py
        health.py
        agents.py
        logs.py
      tests/
        test_health.py
        test_agent_runtime.py
        test_ceo_janie_flow.py
        test_ai_mock_fallback.py
```

## Setup

### Linux/macOS

```bash
./scripts/setup-dev.sh
```

### Windows PowerShell

```powershell
./scripts/setup-dev.ps1
```

## Run Backend

```bash
./scripts/run-backend.sh
```

Or manually:

```bash
cd backend
uvicorn app.main:app --reload
```

## Smoke Test

```bash
./scripts/smoke-test.sh
```

## Manual API Checks

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/agents
curl http://localhost:8000/api/logs

curl -X POST http://localhost:8000/api/agents/message \
  -H "Content-Type: application/json" \
  -d '{
    "from_agent": "ceo",
    "to_agent": "janie",
    "message": "Hello Janie, report system status.",
    "context": {}
  }'
```

## Test

```bash
cd backend
pytest
```

## Notes

- Default AI provider is `mock`.
- `ClaudeAdapter` is optional and safe. If key/SDK is unavailable, it falls back to mock behavior.
- No trading, scheduler, IoT, dashboard, or execution modules are included in Phase 1.
