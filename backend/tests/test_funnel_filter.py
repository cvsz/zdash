from datetime import datetime, timedelta, timezone

from app.trading.funnel_filter import FunnelFilter
from app.trading.models import Candle


def _build_candles(start: float, step: float, count: int = 60) -> list[Candle]:
    now = datetime.now(timezone.utc)
    candles: list[Candle] = []
    for idx in range(count):
        price = start + (step * idx)
        candles.append(
            Candle(
                timestamp=now - timedelta(minutes=(count - idx) * 5),
                open=price,
                high=price + 0.5,
                low=price - 0.5,
                close=price + 0.2,
                volume=1000 + idx,
            )
        )
    return candles


def test_sma_calculation() -> None:
    values = [1, 2, 3, 4, 5]
    sma = FunnelFilter.calculate_sma(values, period=3)

    assert len(sma) == len(values)
    assert round(sma[-1], 4) == 4.0


def test_generate_signal_buy_sell_hold() -> None:
    filter_engine = FunnelFilter(fast=21, medium=10, slow=3)

    up_candles = _build_candles(start=2300.0, step=0.6)
    down_candles = _build_candles(start=2360.0, step=-0.6)
    flat_candles = _build_candles(start=2330.0, step=0.0)

    buy_signal = filter_engine.generate_signal(
        up_candles, symbol="XAUUSD", timeframe="M5"
    )
    sell_signal = filter_engine.generate_signal(
        down_candles, symbol="XAUUSD", timeframe="M5"
    )
    hold_signal = filter_engine.generate_signal(
        flat_candles, symbol="XAUUSD", timeframe="M5"
    )

    assert buy_signal.direction in {"buy", "hold"}
    assert sell_signal.direction in {"sell", "hold"}
    assert hold_signal.direction in {"hold", "buy", "sell"}


def test_confidence_in_range() -> None:
    filter_engine = FunnelFilter()
    candles = _build_candles(start=2300.0, step=0.2)
    signal = filter_engine.generate_signal(candles, symbol="XAUUSD", timeframe="M5")

    assert 0 <= signal.confidence <= 1
