from datetime import datetime, timezone

from app.backtesting.models import Candle
from app.backtesting.strategy_base import BaseStrategy


class DummyStrategy(BaseStrategy):
    name = "dummy"
    default_parameters = {"alpha": 1, "beta": 2}

    def generate_signal(self, candles, index, parameters):
        candle = candles[index]
        return self.hold_signal(
            candle=candle,
            symbol="XAUUSD",
            timeframe="M5",
            metadata={"alpha": self.validate_parameters(parameters)["alpha"]},
        )


def _candle() -> Candle:
    return Candle(
        timestamp=datetime.now(timezone.utc),
        open=2300.0,
        high=2301.0,
        low=2299.0,
        close=2300.4,
        volume=100,
    )


def test_strategy_interface_behavior() -> None:
    strategy = DummyStrategy()
    signal = strategy.generate_signal([_candle()], 0, {})
    assert signal.direction == "hold"
    assert signal.strategy == "dummy"


def test_parameter_validation_merges_defaults() -> None:
    strategy = DummyStrategy()
    params = strategy.validate_parameters({"beta": 5})
    assert params == {"alpha": 1, "beta": 5}


def test_hold_signal_is_allowed() -> None:
    strategy = DummyStrategy()
    signal = strategy.hold_signal(_candle(), "XAUUSD", "M5")
    assert signal.direction == "hold"
    assert signal.entry > 0
