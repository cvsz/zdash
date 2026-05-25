# zDash Phase 3 - Risk System Foundation

Phase 3 adds Guardian-driven risk controls on top of Janie runtime and the trading core.

## Phase 3 Overview

Implemented in this phase:
- Guardian Agent (`guardian`) for risk approval decisions
- DrawdownGuard for total and daily drawdown evaluation
- In-memory HaltFlagStore for emergency/manual halts
- KillSwitch for emergency threshold activation
- GuardianService orchestration layer
- ExecutionEngine risk gating
- Risk API endpoints
- Risk-specific tests

Safety defaults:
- `DRY_RUN=true`
- `LIVE_TRADING_ACK=false`
- `RISK_GUARDIAN_ENABLED=true`

## Risk Architecture

Core components:
- `backend/app/risk/models.py`
- `backend/app/risk/drawdown_guard.py`
- `backend/app/risk/halt_flag.py`
- `backend/app/risk/kill_switch.py`
- `backend/app/risk/guardian_service.py`
- `backend/app/agents/guardian.py`

Execution flow:
1. Execution request enters `ExecutionEngine`.
2. `GuardianService.approve_execution()` evaluates snapshot.
3. If halt active or drawdown unsafe -> execution blocked.
4. If safe and `DRY_RUN=true` -> simulated execution.
5. If `DRY_RUN=false`, config gates are enforced.

## Drawdown Formulas

Total drawdown:

```text
total_drawdown_percent = ((peak_equity - current_equity) / peak_equity) * 100
```

Daily drawdown:

```text
daily_drawdown_percent = ((daily_start_equity - current_equity) / daily_start_equity) * 100
```

Safety behavior:
- Drawdown is clamped at `>= 0`
- Rounded to 4 decimals
- Invalid baseline equity (<=0) falls back safely with warning state

## Risk API

- `GET /api/risk/status`
- `POST /api/risk/check`
- `GET /api/risk/drawdown`
- `POST /api/risk/halt`
- `POST /api/risk/resume`
- `POST /api/risk/approve-execution`

### Check Risk

```bash
curl -X POST http://localhost:8000/api/risk/check \
  -H "Content-Type: application/json" \
  -d '{
    "balance": 10000,
    "equity": 9500,
    "peak_equity": 10000,
    "daily_start_equity": 10000,
    "open_positions": 0,
    "floating_pnl": -500,
    "realized_pnl_today": -500
  }'
```

### Manual Halt

```bash
curl -X POST http://localhost:8000/api/risk/halt \
  -H "Content-Type: application/json" \
  -d '{"reason": "Manual operator halt"}'
```

### Resume

```bash
curl -X POST http://localhost:8000/api/risk/resume \
  -H "Content-Type: application/json" \
  -d '{"reason": "Reviewed and safe for dry-run resume"}'
```

## Setup

```bash
./scripts/setup-dev.sh
source .venv/bin/activate
```

## Run Backend

```bash
./scripts/run-backend.sh
```

Or:

```bash
cd backend
uvicorn app.main:app --reload
```

## Test

```bash
cd backend
pytest
```

## Safety Notes

- This implementation is for simulation/paper-trading guarded automation.
- No financial advice is provided.
- Live execution is blocked unless configuration gates explicitly permit it.
