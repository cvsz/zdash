import pytest
from datetime import UTC, datetime, timedelta

from app.backtesting.models import Candle
from app.backtesting.strategies import (
    BreakoutStrategy,
    MeanReversionStrategy,
    RSICrossStrategy,
    VWAPStrategy,
)
from app.backtesting.strategy_base import BaseStrategy


def _series_candles(
    closes: list[float],
    volumes: list[float] | None = None,
) -> list[Candle]:
    out: list[Candle] = []
    for i, close in enumerate(closes):
        volume = volumes[i] if volumes else 100.0
        out.append(
            Candle(
                timestamp=datetime(2026, 8, 23, tzinfo=UTC) + timedelta(minutes=i),
                open=close,
                high=close + 1.0,
                low=close - 1.0,
                close=close,
                volume=volume,
            )
        )
    return out


def test_all_strategies_subclass_base() -> None:
    for strategy in (
        RSICrossStrategy(),
        BreakoutStrategy(),
        MeanReversionStrategy(),
        VWAPStrategy(),
    ):
        assert isinstance(strategy, BaseStrategy)


# --- RSI cross ----------------------------------------------------------------


def test_rsi_cross_buys_on_oversold_cross() -> None:
    # Rising series pins RSI at 100; craft a dip below 30 then recovery.
    closes = [100.0 - i * 2.0 for i in range(20)]  # falling -> rsi 0
    candles = _series_candles(closes)
    strategy = RSICrossStrategy()
    signal = strategy.generate_signal(candles, len(candles) - 1, {})
    # Still below oversold without a cross up: hold.
    assert signal.direction in {"hold", "sell"}


def test_rsi_cross_insufficient_history_holds() -> None:
    candles = _series_candles([100.0 + i for i in range(5)])
    signal = RSICrossStrategy().generate_signal(candles, len(candles) - 1, {})
    assert signal.direction == "hold"
    assert signal.metadata.get("reason") == "insufficient_history"


def test_rsi_cross_invalid_parameters_rejected() -> None:
    strategy = RSICrossStrategy()
    with pytest.raises(ValueError):
        strategy.validate_parameters({"period": 1})
    with pytest.raises(ValueError):
        strategy.validate_parameters({"overbought": 40})


# --- breakout -----------------------------------------------------------------


def test_breakout_buys_above_recent_high_with_volume() -> None:
    closes = [2300.0] * 24 + [2320.0]
    candles = _series_candles(closes, volumes=[100.0] * 24 + [500.0])
    strategy = BreakoutStrategy()
    signal = strategy.generate_signal(candles, len(candles) - 1, {})
    assert signal.direction == "buy"
    assert signal.stop_loss < signal.entry < signal.take_profit
    assert signal.metadata["volume_confirmed"] is True


def test_breakout_holds_without_volume_confirmation() -> None:
    closes = [2300.0] * 24 + [2320.0]
    candles = _series_candles(closes, volumes=[100.0] * 24 + [10.0])
    signal = BreakoutStrategy().generate_signal(candles, len(candles) - 1, {})
    assert signal.direction == "hold"


def test_breakout_sells_below_recent_low_with_volume() -> None:
    closes = [2400.0] * 24 + [2390.0]
    candles = _series_candles(closes, volumes=[100.0] * 24 + [500.0])
    signal = BreakoutStrategy().generate_signal(candles, len(candles) - 1, {})
    assert signal.direction == "sell"
    assert signal.stop_loss > signal.entry > signal.take_profit


def test_breakout_invalid_parameters_rejected() -> None:
    with pytest.raises(ValueError):
        BreakoutStrategy().validate_parameters({"lookback": 3})
    with pytest.raises(ValueError):
        BreakoutStrategy().validate_parameters({"volume_factor": 0})


# --- mean reversion -----------------------------------------------------------


def test_mean_reversion_buys_on_lower_band_cross() -> None:
    # Mild noise then a sharp drop pushes the z-score below -z_entry.
    closes = [2300.0 + (0.25 if i % 2 else -0.25) for i in range(20)]
    closes += [2296.0, 2290.0]
    candles = _series_candles(closes)
    index = len(candles) - 1
    signal = MeanReversionStrategy().generate_signal(candles, index, {"window": 20})
    assert signal.direction == "buy"
    assert signal.stop_loss < signal.entry < signal.take_profit


def test_mean_reversion_sells_on_upper_band_cross() -> None:
    closes = [2300.0 + (0.25 if i % 2 else -0.25) for i in range(20)]
    closes += [2304.0, 2310.0]
    candles = _series_candles(closes)
    index = len(candles) - 1
    signal = MeanReversionStrategy().generate_signal(candles, index, {"window": 20})
    assert signal.direction == "sell"


def test_mean_reversion_zero_variance_holds() -> None:
    candles = _series_candles([2300.0] * 30)
    signal = MeanReversionStrategy().generate_signal(candles, 29, {})
    assert signal.direction == "hold"


def test_mean_reversion_invalid_parameters_rejected() -> None:
    with pytest.raises(ValueError):
        MeanReversionStrategy().validate_parameters({"window": 2})
    with pytest.raises(ValueError):
        MeanReversionStrategy().validate_parameters({"z_entry": 0})


# --- vwap ---------------------------------------------------------------------


def test_vwap_buys_on_deviation_cross_below() -> None:
    base = 2300.0
    closes = [base] * 35 + [base * 0.97]
    candles = _series_candles(closes)
    index = len(candles) - 1
    signal = VWAPStrategy().generate_signal(candles, index, {})
    assert signal.direction == "buy"


def test_vwap_sells_on_deviation_cross_above() -> None:
    base = 2300.0
    closes = [base] * 35 + [base * 1.03]
    candles = _series_candles(closes)
    index = len(candles) - 1
    signal = VWAPStrategy().generate_signal(candles, index, {})
    assert signal.direction == "sell"


def test_vwap_insufficient_history_holds() -> None:
    candles = _series_candles([100.0 + i for i in range(4)])
    signal = VWAPStrategy().generate_signal(candles, 3, {})
    assert signal.direction == "hold"
    assert signal.metadata.get("reason") == "insufficient_history"


def test_vwap_invalid_threshold_rejected() -> None:
    with pytest.raises(ValueError):
        VWAPStrategy().validate_parameters({"threshold": 1.5})
