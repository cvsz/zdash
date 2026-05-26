import pytest

from app.backtesting.models import BacktestRequest
from app.backtesting.strategy_lab import StrategyLab


def test_run_mock_backtest_generates_result() -> None:
    lab = StrategyLab()
    result = lab.run_backtest(BacktestRequest(strategy="ob_aggressive"))
    assert result.strategy == "ob_aggressive"
    assert result.final_balance > 0


def test_backtest_generates_trades_and_final_balance() -> None:
    lab = StrategyLab()
    result = lab.run_backtest(BacktestRequest(strategy="ob_aggressive"))
    closed_trades = [trade for trade in result.trades if trade.status == "closed"]
    assert closed_trades
    assert result.final_balance == pytest.approx(result.initial_balance + sum(trade.pnl for trade in closed_trades), rel=1e-4)


def test_backtest_has_no_overlapping_trades() -> None:
    lab = StrategyLab()
    result = lab.run_backtest(BacktestRequest(strategy="ob_aggressive"))
    closed_trades = [trade for trade in result.trades if trade.status == "closed"]
    for prior, current in zip(closed_trades, closed_trades[1:]):
        assert prior.exit_time is not None
        assert current.entry_time >= prior.exit_time


def test_invalid_strategy_returns_clean_error() -> None:
    lab = StrategyLab()
    with pytest.raises(ValueError, match="Unknown strategy"):
        lab.run_backtest(BacktestRequest(strategy="unknown_strategy"))
