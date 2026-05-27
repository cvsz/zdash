from datetime import datetime, timezone

import pytest

from app.trading.models import Candle, ExecutionRequest, TradingSignal


def test_candle_validation() -> None:
    candle = Candle(
        timestamp=datetime.now(timezone.utc),
        open=2300.0,
        high=2302.0,
        low=2298.0,
        close=2301.0,
        volume=1000,
    )
    assert candle.high >= candle.close


def test_candle_invalid_bounds() -> None:
    with pytest.raises(ValueError):
        Candle(
            timestamp=datetime.now(timezone.utc),
            open=2300.0,
            high=2299.0,
            low=2298.0,
            close=2301.0,
            volume=1000,
        )


def test_trading_signal_direction_validation() -> None:
    with pytest.raises(ValueError):
        TradingSignal(
            symbol="XAUUSD",
            timeframe="M5",
            direction="neutral",
            strategy="ob_aggressive",
            confidence=0.6,
            entry=2300.0,
            stop_loss=2298.0,
            take_profit=2304.0,
            reason="test",
        )


def test_execution_request_defaults_to_dry_run() -> None:
    signal = TradingSignal(
        symbol="XAUUSD",
        timeframe="M5",
        direction="buy",
        strategy="ob_aggressive",
        confidence=0.7,
        entry=2300.0,
        stop_loss=2298.0,
        take_profit=2304.0,
        reason="model test",
    )
    request = ExecutionRequest(signal=signal)
    assert request.dry_run is True
