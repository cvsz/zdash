from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.backtesting.models import BacktestRequest, Candle, OptimizationRequest, StrategySignal


def test_candle_validation_accepts_valid_ohlc() -> None:
    candle = Candle(
        timestamp=datetime.now(timezone.utc),
        open=2300.0,
        high=2301.0,
        low=2299.5,
        close=2300.4,
        volume=100.0,
    )
    assert candle.high >= candle.open
    assert candle.low <= candle.close


def test_candle_validation_rejects_invalid_ohlc() -> None:
    with pytest.raises(ValidationError):
        Candle(
            timestamp=datetime.now(timezone.utc),
            open=2300.0,
            high=2299.0,
            low=2298.0,
            close=2299.5,
            volume=100.0,
        )


def test_strategy_signal_direction_validation() -> None:
    with pytest.raises(ValidationError):
        StrategySignal(
            timestamp=datetime.now(timezone.utc),
            symbol="XAUUSD",
            timeframe="M5",
            strategy="ob_aggressive",
            direction="invalid",
            entry=2300.0,
            stop_loss=2299.0,
            take_profit=2301.0,
            confidence=0.7,
        )


def test_backtest_request_defaults() -> None:
    request = BacktestRequest(strategy="ob_aggressive")
    assert request.symbol == "XAUUSD"
    assert request.timeframe == "M5"
    assert request.dataset == "mock"
    assert request.initial_balance == 10000
    assert request.risk_per_trade_percent == 1


def test_optimization_request_max_combinations_validation() -> None:
    with pytest.raises(ValidationError):
        OptimizationRequest(
            strategy="ob_aggressive",
            parameter_grid={"lookback": [8, 12]},
            max_combinations=0,
        )
