from datetime import datetime, timezone

from app.backtesting.models import BacktestMetrics, BacktestRequest, BacktestResult
from app.backtesting.promotion import StrategyPromotionGate
from app.core.config import get_settings


def _result_with_metrics(metrics: BacktestMetrics) -> BacktestResult:
    now = datetime.now(timezone.utc)
    request = BacktestRequest(strategy="ob_aggressive")
    return BacktestResult(
        id="result-1",
        request=request,
        strategy=request.strategy,
        symbol=request.symbol,
        timeframe=request.timeframe,
        initial_balance=10000,
        final_balance=10100,
        metrics=metrics,
        trades=[],
        parameters={},
        started_at=now,
        finished_at=now,
        duration_ms=1,
    )


def _metrics(
    *,
    total_trades: int = 60,
    win_rate: float = 55.0,
    profit_factor: float = 1.4,
    max_drawdown_percent: float = 10.0,
    consecutive_losses: int = 3,
) -> BacktestMetrics:
    return BacktestMetrics(
        total_trades=total_trades,
        winning_trades=35,
        losing_trades=25,
        win_rate=win_rate,
        gross_profit=1200,
        gross_loss=800,
        net_profit=400,
        net_profit_percent=4.0,
        profit_factor=profit_factor,
        max_drawdown_percent=max_drawdown_percent,
        average_rr=1.2,
        expectancy=6.0,
        sharpe_like_score=0.8,
        consecutive_losses=consecutive_losses,
        monthly_return_table={"2026-01": 300},
    )


def test_promotion_disabled_blocks_approval(monkeypatch) -> None:
    monkeypatch.setenv("ALLOW_STRATEGY_PROMOTION", "false")
    get_settings.cache_clear()
    decision = StrategyPromotionGate().evaluate(_result_with_metrics(_metrics()))
    assert decision.approved is False
    assert decision.reason == "promotion_disabled_by_config"


def test_insufficient_trades_blocks_approval(monkeypatch) -> None:
    monkeypatch.setenv("ALLOW_STRATEGY_PROMOTION", "true")
    get_settings.cache_clear()
    decision = StrategyPromotionGate().evaluate(_result_with_metrics(_metrics(total_trades=20)))
    assert decision.approved is False
    assert decision.reason == "insufficient_trades"


def test_high_drawdown_blocks_approval(monkeypatch) -> None:
    monkeypatch.setenv("ALLOW_STRATEGY_PROMOTION", "true")
    get_settings.cache_clear()
    decision = StrategyPromotionGate().evaluate(
        _result_with_metrics(_metrics(max_drawdown_percent=45.0, total_trades=120))
    )
    assert decision.approved is False
    assert decision.reason == "drawdown_above_threshold"


def test_valid_metrics_approve_only_when_enabled(monkeypatch) -> None:
    monkeypatch.setenv("ALLOW_STRATEGY_PROMOTION", "true")
    get_settings.cache_clear()
    decision = StrategyPromotionGate().evaluate(_result_with_metrics(_metrics(total_trades=120)))
    assert decision.approved is True
    assert decision.reason == "approved"
