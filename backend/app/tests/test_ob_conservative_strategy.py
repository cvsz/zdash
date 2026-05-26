from app.backtesting.datasets import MockDatasetProvider
from app.backtesting.strategies.ob_aggressive import OBAggressiveStrategy
from app.backtesting.strategies.ob_conservative import OBConservativeStrategy


def test_ob_conservative_returns_valid_signals() -> None:
    strategy = OBConservativeStrategy()
    candles = MockDatasetProvider().load("mock", "XAUUSD", "M5")
    signals = [strategy.generate_signal(candles, index, {}) for index in range(len(candles))]
    actionable = [signal for signal in signals if signal.direction in {"buy", "sell"}]
    for signal in actionable:
        if signal.direction == "buy":
            assert signal.stop_loss < signal.entry < signal.take_profit
        else:
            assert signal.take_profit < signal.entry < signal.stop_loss


def test_ob_conservative_lower_frequency_than_aggressive() -> None:
    candles = MockDatasetProvider().load("mock", "XAUUSD", "M5")
    conservative = OBConservativeStrategy()
    aggressive = OBAggressiveStrategy()

    conservative_count = sum(
        1
        for index in range(len(candles))
        if conservative.generate_signal(candles, index, {}).direction in {"buy", "sell"}
    )
    aggressive_count = sum(
        1
        for index in range(len(candles))
        if aggressive.generate_signal(candles, index, {}).direction in {"buy", "sell"}
    )

    assert conservative_count < aggressive_count


def test_ob_conservative_parameters_validate() -> None:
    strategy = OBConservativeStrategy()
    params = strategy.validate_parameters({"confidence_threshold": 0.75})
    assert params["lookback"] == 24
    assert params["confidence_threshold"] == 0.75
