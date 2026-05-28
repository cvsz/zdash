# Phase 33 · AI Trader Simulation Layer

Phase 33 adds a deterministic, safety-first AI Trader Simulation layer to zDash.

## Scope

The AI Trader module generates `TradingSignal` objects from OHLCV candle data and routes every result through existing zDash safety systems:

- `TradingService`
- `SignalValidationService`
- `ExecutionEngine`
- Guardian risk checks
- RBAC dependencies
- dry-run execution behavior

## Safety posture

This phase is simulation-only.

- No live trading is enabled.
- No real broker order execution is added.
- No external ML dependencies are added.
- Every generated signal includes `simulation_only=true` metadata.
- Every generated signal includes a safety notice.
- Paper-trade execution forces `dry_run=true`.
- Live trading remains disabled by default.

Nothing in this module is financial advice.

## Backend files

```text
backend/app/ai_trader/__init__.py
backend/app/ai_trader/service.py
backend/app/api/ai_trader.py
backend/tests/test_ai_trader_service.py
```

Router registration:

```text
backend/app/main.py
```

## API

All examples use backend port `8005`.

```bash
curl http://localhost:8005/api/ai-trader/status -H "Authorization: Bearer TOKEN"
```

```bash
curl -X POST http://localhost:8005/api/ai-trader/signal \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "XAUUSD",
    "timeframe": "M5",
    "candles": [],
    "min_confidence": 0.55
  }'
```

```bash
curl -X POST http://localhost:8005/api/ai-trader/paper-trade \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "XAUUSD",
    "timeframe": "M5",
    "candles": [],
    "min_confidence": 0.55
  }'
```

## Deterministic features

`AITraderService` computes:

- latest close price
- fast moving average, default 7 candles
- slow moving average, default 21 candles
- 3-candle momentum
- average true range proxy
- volatility percentage

If candle count is insufficient, the service returns a `hold` signal. If confidence is below the configured `min_confidence`, it returns a `hold` signal.

## Frontend

Frontend additions:

```text
frontend/src/api/aiTrader.ts
frontend/src/components/trading/AITraderSimulationCard.tsx
frontend/src/pages/XauDashboard.tsx
```

The `/xau` dashboard shows:

- AI Trader Simulation card
- model version
- generated direction
- confidence
- validation state
- dry-run paper-trade result
- visible simulation-only banner

## Validation

```bash
cd backend
source .venv/bin/activate
python -m ruff check app tests
python -B -m pytest -q

cd ../frontend
source ~/.nvm/nvm.sh
nvm use 20
npm test
npm run build
```

Full repository validation:

```bash
cd ~/zdash
make validate
```
