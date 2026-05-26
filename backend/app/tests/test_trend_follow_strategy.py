from datetime import datetime, timedelta, timezone

import pytest

from app.backtesting.models import Candle
from app.backtesting.strategies.trend_follow import TrendFollowStrategy


def _build_cross_dataset() -> list[Candle]:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    candles: list[Candle] = []
    price = 2200.0
    for i in range(40):
        if i < 20:
            close = price - 0.2
        else:
            close = price + 1.8
        high = max(price, close) + 0.05
        low = min(price, close) - 0.05
        candles.append(
            Candle(
                timestamp=start + timedelta(minutes=5 * i),
                open=price,
                high=high,
                low=low,
                close=close,
                volume=120,
            )
        )
        price = close
    return candles


def test_trend_follow_moving_average_windows_validate() -> None:
    strategy = TrendFollowStrategy()
    with pytest.raises(ValueError):
        strategy.validate_parameters({"short_window": 30, "long_window": 10})


def test_trend_follow_returns_hold_until_enough_candles() -> None:
    strategy = TrendFollowStrategy()
    candles = _build_cross_dataset()
    signal = strategy.generate_signal(candles, 5, {})
    assert signal.direction == "hold"


def test_trend_follow_cross_signals_are_valid() -> None:
    strategy = TrendFollowStrategy()
    candles = _build_cross_dataset()
    params = {"short_window": 3, "long_window": 7, "confidence_threshold": 0.0}
    signals = [strategy.generate_signal(candles, index, params) for index in range(len(candles))]
    actionable = [signal for signal in signals if signal.direction in {"buy", "sell"}]
    assert actionable
    for signal in actionable:
        if signal.direction == "buy":
            assert signal.stop_loss < signal.entry < signal.take_profit
        else:
            assert signal.take_profit < signal.entry < signal.stop_loss
