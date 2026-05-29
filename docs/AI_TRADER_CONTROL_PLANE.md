# AI Trader Control Plane

The AI Trader Control Plane is a simulation-grade trading analysis layer for zDash. It produces deterministic strategy signals from OHLCV candle data and routes paper-trade execution through the existing safety stack.

## Safety policy

- Simulation only.
- Not financial advice.
- No live broker execution.
- No guaranteed profit claims.
- `dry_run=true` is forced for paper-trade execution.
- Guardian risk checks remain mandatory.
- `SignalValidationService` remains mandatory.
- `TradingService` and `ExecutionEngine` remain the execution path.
- RBAC, audit/event logging, and dry-run mode are not bypassed.

## Architecture

```text
API router
  -> AITraderService
    -> strategy registry
    -> feature engine
    -> deterministic decision engine
    -> SignalValidationService via TradingService
    -> ExecutionEngine dry-run paper trade
    -> Guardian risk checks
    -> Event bus
```

## Strategy registry

Default strategies:

| Strategy | Risk profile | Behavior |
|---|---|---|
| `trend_momentum_v1` | balanced | Uses moving-average trend and momentum alignment. |
| `mean_reversion_v1` | moderate | Looks for price extension against slow moving average with stabilizing momentum. |
| `volatility_breakout_v1` | aggressive | Requires volatility and momentum agreement. |
| `conservative_guarded_v1` | conservative | Prefers hold decisions and requires stronger confidence. |

All strategies expose:

- `id`
- `name`
- `description`
- `risk_profile`
- `min_candles`
- `default_min_confidence`
- `supported_symbols`
- `supported_timeframes`
- `simulation_only=true`

## Feature engine

Pure Python features, no external ML dependency:

- close
- fast moving average
- slow moving average
- moving-average delta
- 3-candle momentum
- 7-candle momentum
- volatility percentage
- ATR proxy
- volume moving average
- volume ratio
- trend state
- volatility state

Malformed or insufficient data returns stable defaults and warnings instead of crashing normal requests.

## API endpoints

All examples use backend port `8005`.

```bash
curl http://localhost:8005/api/ai-trader/status -H "Authorization: Bearer TOKEN"
curl http://localhost:8005/api/ai-trader/strategies -H "Authorization: Bearer TOKEN"
```

```bash
curl -X POST http://localhost:8005/api/ai-trader/signal \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "XAUUSD",
    "timeframe": "M5",
    "strategy_id": "trend_momentum_v1",
    "candles": [],
    "min_confidence": 0.55
  }'
```

```bash
curl -X POST http://localhost:8005/api/ai-trader/compare \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "XAUUSD",
    "timeframe": "M5",
    "candles": [],
    "strategy_ids": ["trend_momentum_v1", "mean_reversion_v1"]
  }'
```

```bash
curl -X POST http://localhost:8005/api/ai-trader/paper-trade \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "XAUUSD",
    "timeframe": "M5",
    "strategy_id": "trend_momentum_v1",
    "candles": [],
    "min_confidence": 0.55
  }'
```

## Metadata guarantee

Every generated signal includes:

```json
{
  "model_version": "ai-trader-phase34",
  "strategy_id": "trend_momentum_v1",
  "simulation_only": true,
  "safety_notice": "Simulation only. Not financial advice. No live execution.",
  "features": {},
  "warnings": [],
  "explanation": "...",
  "risk_policy": {
    "dry_run_forced": true,
    "guardian_required": true,
    "live_execution_allowed": false
  }
}
```

## Backtest-to-paper workflow

1. Use Strategy Lab/backtesting to research candidate logic.
2. Keep results as simulation-only evidence.
3. Compare AI Trader strategies through `/api/ai-trader/compare`.
4. Generate a signal through `/api/ai-trader/signal`.
5. Run paper trade through `/api/ai-trader/paper-trade`.
6. Execution remains dry-run only and must pass validation/Guardian checks.

## Frontend panel

The XAU dashboard includes the AI Trader Control Plane card:

- simulation-only banner
- strategy selector
- symbol/timeframe/min-confidence inputs
- generated direction and confidence
- validation state
- strategy comparison table
- dry-run-only paper-trade button
- no live trading button

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

Full local validation:

```bash
cd ~/zdash
make validate-fast
make validate
```
