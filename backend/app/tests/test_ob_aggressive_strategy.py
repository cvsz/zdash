from app.backtesting.datasets import MockDatasetProvider
from app.backtesting.strategies.ob_aggressive import OBAggressiveStrategy


def test_ob_aggressive_returns_valid_signals() -> None:
    strategy = OBAggressiveStrategy()
    candles = MockDatasetProvider().load("mock", "XAUUSD", "M5")
    signals = [
        strategy.generate_signal(candles, index, {}) for index in range(len(candles))
    ]
    actionable = [signal for signal in signals if signal.direction in {"buy", "sell"}]
    assert actionable
    for signal in actionable:
        if signal.direction == "buy":
            assert signal.stop_loss < signal.entry < signal.take_profit
        else:
            assert signal.take_profit < signal.entry < signal.stop_loss


def test_ob_aggressive_parameters_validate() -> None:
    strategy = OBAggressiveStrategy()
    params = strategy.validate_parameters({"lookback": 14})
    assert params["lookback"] == 14
    assert params["risk_reward"] == 2.0


def test_ob_aggressive_confidence_range_and_levels() -> None:
    strategy = OBAggressiveStrategy()
    candles = MockDatasetProvider().load("mock", "XAUUSD", "M5")
    signal = strategy.generate_signal(candles, 40, {})
    assert 0 <= signal.confidence <= 1
    assert signal.stop_loss > 0
    assert signal.take_profit > 0
