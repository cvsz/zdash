from app.backtesting.backtest_service import get_backtest_service
from app.backtesting.models import BacktestRequest


def test_backtesting_smoke() -> None:
    service = get_backtest_service()
    result = service.run_backtest(BacktestRequest(strategy="ob_aggressive"))
    assert result.strategy == "ob_aggressive"
    assert result.symbol == "XAUUSD"
