from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.ai_trader.service import AITraderService
from app.risk.models import AccountSnapshot
from app.trading.models import Candle


def _candles(direction: str = "up", count: int = 30) -> list[Candle]:
    now = datetime.now(timezone.utc)
    items: list[Candle] = []
    base = 2300.0
    for i in range(count):
        step = i * 1.2 if direction == "up" else -i * 1.2
        close = base + step
        open_price = close - 0.4 if direction == "up" else close + 0.4
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


def test_upward_trend_can_generate_buy_or_hold_but_is_simulation_only() -> None:
    service = AITraderService()
    signal = service.generate_signal(_candles("up"), min_confidence=0.55)

    assert signal.direction in {"buy", "hold"}
    assert signal.metadata["simulation_only"] is True
    assert "Not financial advice" in signal.metadata["safety_notice"]
    assert signal.metadata["model_version"] == service.model_version


def test_downward_trend_can_generate_sell_or_hold() -> None:
    service = AITraderService()
    signal = service.generate_signal(_candles("down"), min_confidence=0.55)

    assert signal.direction in {"sell", "hold"}
    assert signal.metadata["simulation_only"] is True


def test_insufficient_candles_returns_hold() -> None:
    service = AITraderService()
    signal = service.generate_signal(_candles("up", count=5), min_confidence=0.55)

    assert signal.direction == "hold"
    assert "insufficient candles" in signal.reason
    assert signal.metadata["simulation_only"] is True


def test_paper_trade_result_is_always_dry_run() -> None:
    service = AITraderService()
    result = service.paper_trade(
        candles=_candles("up"),
        symbol="XAUUSD",
        timeframe="M5",
        min_confidence=0.55,
        snapshot=_snapshot(),
    )

    execution = result["execution"]
    assert result["dry_run"] is True
    assert execution.dry_run is True
    assert execution.status in {
        "simulated",
        "blocked_by_validation",
        "blocked_by_risk",
        "blocked_by_config",
    }
    assert result["signal"].metadata["simulation_only"] is True
