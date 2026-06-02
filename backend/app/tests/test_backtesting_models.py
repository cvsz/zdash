from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.backtesting.models import (
    BacktestRequest,
    Candle,
    OptimizationRequest,
    StrategySignal,
)


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
        StrategySignal.model_validate(
            {
                "timestamp": datetime.now(timezone.utc),
                "symbol": "XAUUSD",
                "timeframe": "M5",
                "strategy": "ob_aggressive",
                "direction": "invalid",
                "entry": 2300.0,
                "stop_loss": 2299.0,
                "take_profit": 2301.0,
                "confidence": 0.7,
            }
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


def test_optimization_request_defaults_empty_parameter_grid():
    from app.backtesting.models import OptimizationRequest

    req = OptimizationRequest(
        strategy="ob_aggressive",
        symbol="XAUUSD",
        timeframe="M5",
        sort_metric="max_drawdown_percent",
    )

    assert req.parameter_grid == {}


def test_optimizer_accepts_empty_parameter_grid():
    from app.backtesting.models import OptimizationRequest
    from app.backtesting.optimizer import ParameterOptimizer

    req = OptimizationRequest(
        strategy="ob_aggressive",
        symbol="XAUUSD",
        timeframe="M5",
        parameter_grid={},
        sort_metric="profit_factor",
    )

    result = ParameterOptimizer().optimize(req)

    assert result.executed_combinations == 1
    assert result.total_combinations == 1


def test_optimizer_accepts_max_drawdown_percent_sort_metric():
    from app.backtesting.models import OptimizationRequest
    from app.backtesting.optimizer import ParameterOptimizer

    req = OptimizationRequest(
        strategy="ob_aggressive",
        symbol="XAUUSD",
        timeframe="M5",
        parameter_grid={"lookback": [8, 12], "risk_reward": [1.5, 2.0]},
        sort_metric="max_drawdown_percent",
        max_combinations=4,
    )

    result = ParameterOptimizer().optimize(req)

    assert result.sort_metric == "max_drawdown_percent"
    assert len(result.ranked_results) == 4

    drawdowns = [r.metrics.max_drawdown_percent for r in result.ranked_results]
    assert drawdowns == sorted(drawdowns), "max_drawdown_percent should sort ascending"
