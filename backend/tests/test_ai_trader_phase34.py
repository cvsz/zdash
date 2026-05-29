from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.ai_trader.service import AITraderService
from app.main import app
from app.risk.models import AccountSnapshot
from app.trading.models import Candle


def _candles(direction: str = "up", count: int = 34) -> list[Candle]:
    now = datetime.now(timezone.utc)
    items: list[Candle] = []
    base = 2300.0
    for i in range(count):
        step = i * 1.1 if direction == "up" else -i * 1.1
        close = base + step
        open_price = close - 0.35 if direction == "up" else close + 0.35
        high = max(open_price, close) + 0.8
        low = min(open_price, close) - 0.8
        items.append(
            Candle(
                timestamp=now + timedelta(minutes=i * 5),
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=100 + i,
            )
        )
    return items


def _payload(direction: str = "up", count: int = 34, strategy_id: str = "trend_momentum_v1") -> dict:
    return {
        "symbol": "XAUUSD",
        "timeframe": "M5",
        "strategy_id": strategy_id,
        "candles": [candle.model_dump(mode="json") for candle in _candles(direction, count)],
        "min_confidence": 0.55,
    }


def _snapshot() -> AccountSnapshot:
    return AccountSnapshot(
        balance=10000,
        equity=10000,
        peak_equity=10000,
        daily_start_equity=10000,
        open_positions=0,
        floating_pnl=0,
        realized_pnl_today=0,
    )


def test_status_endpoint_reports_simulation_only() -> None:
    client = TestClient(app)
    response = client.get("/api/ai-trader/status")
    assert response.status_code in {200, 401, 403}
    if response.status_code == 200:
        data = response.json()["data"]
        assert data["simulation_only"] is True
        assert data["live_execution_allowed"] is False
        assert data["dry_run_forced"] is True


def test_strategies_endpoint_returns_default_registry() -> None:
    service = AITraderService()
    ids = {strategy.id for strategy in service.list_strategies()}
    assert ids == {
        "trend_momentum_v1",
        "mean_reversion_v1",
        "volatility_breakout_v1",
        "conservative_guarded_v1",
    }
    assert all(strategy.simulation_only for strategy in service.list_strategies())


def test_insufficient_candles_returns_hold() -> None:
    service = AITraderService()
    signal = service.generate_signal(_candles("up", count=5), strategy_id="trend_momentum_v1")
    assert signal.direction == "hold"
    assert signal.metadata["simulation_only"] is True
    assert signal.metadata["risk_policy"]["live_execution_allowed"] is False


def test_trend_up_generates_buy_or_hold() -> None:
    service = AITraderService()
    signal = service.generate_signal(_candles("up"), strategy_id="trend_momentum_v1")
    assert signal.direction in {"buy", "hold"}
    assert signal.metadata["strategy_id"] == "trend_momentum_v1"


def test_trend_down_generates_sell_or_hold() -> None:
    service = AITraderService()
    signal = service.generate_signal(_candles("down"), strategy_id="trend_momentum_v1")
    assert signal.direction in {"sell", "hold"}
    assert signal.metadata["simulation_only"] is True


def test_compare_returns_ranked_decisions() -> None:
    service = AITraderService()
    result = service.compare_strategies(
        candles=_candles("up"),
        strategy_ids=["trend_momentum_v1", "mean_reversion_v1"],
    )
    assert result["simulation_only"] is True
    assert len(result["ranked_decisions"]) == 2
    assert result["ranked_decisions"][0]["signal"].metadata["simulation_only"] is True


def test_paper_trade_always_returns_dry_run_and_never_live_execution() -> None:
    service = AITraderService()
    result = service.paper_trade(
        candles=_candles("up"),
        strategy_id="trend_momentum_v1",
        snapshot=_snapshot(),
    )
    execution = result["execution"]
    assert result["dry_run"] is True
    assert result["live_execution_allowed"] is False
    assert execution.dry_run is True
    assert result["signal"].metadata["risk_policy"]["live_execution_allowed"] is False


def test_malformed_candles_do_not_crash_service() -> None:
    service = AITraderService()
    candles = _candles("up", count=3)
    candles[0] = candles[0].model_copy(update={"close": -1, "high": -1, "low": -2})
    signal = service.generate_signal(candles, strategy_id="conservative_guarded_v1")
    assert signal.direction == "hold"
    assert signal.metadata["simulation_only"] is True
    assert isinstance(signal.metadata["warnings"], list)


def test_every_signal_metadata_has_simulation_only() -> None:
    service = AITraderService()
    for strategy in service.list_strategies():
        signal = service.generate_signal(_candles("up"), strategy_id=strategy.id)
        assert signal.metadata["simulation_only"] is True
        assert signal.metadata["risk_policy"]["dry_run_forced"] is True
