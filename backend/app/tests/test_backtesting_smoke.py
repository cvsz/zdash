from fastapi.testclient import TestClient

from app.backtesting.backtest_service import backtest_service
from app.backtesting.datasets import MockDatasetProvider
from app.backtesting.models import BacktestRequest, Candle, OptimizationRequest
from app.backtesting.optimizer import ParameterOptimizer
from app.main import app


def test_candle_validation():
    c = Candle(timestamp="2026-01-01T00:00:00+00:00", open=1, high=2, low=0.5, close=1.5)
    assert c.high >= c.open


def test_mock_deterministic():
    a = MockDatasetProvider().load("mock", "XAUUSD", "M5")
    b = MockDatasetProvider().load("mock", "XAUUSD", "M5")
    assert len(a) >= 300
    assert a[5].close == b[5].close


def test_backtest_and_optimize():
    result = backtest_service.run_backtest(BacktestRequest(strategy="ob_aggressive"))
    assert result.metrics.total_trades >= 0
    opt = ParameterOptimizer().optimize(OptimizationRequest(strategy="ob_aggressive", parameter_grid={"lookback": [8, 12], "risk_reward": [1.5]}))
    assert opt.executed_combinations == 2


def test_api_endpoints():
    c = TestClient(app)
    assert c.get('/api/backtesting/status').status_code == 200
    run = c.post('/api/backtesting/run', json={"strategy": "ob_aggressive"})
    assert run.status_code == 200
