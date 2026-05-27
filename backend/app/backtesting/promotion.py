from __future__ import annotations

from datetime import datetime, timezone

from app.backtesting.models import BacktestResult, StrategyPromotionDecision
from app.core.config import get_settings


class StrategyPromotionGate:
    def evaluate(self, result: BacktestResult) -> StrategyPromotionDecision:
        settings = get_settings()
        metrics = result.metrics
        gates = {
            "allow_promotion": settings.allow_strategy_promotion,
            "min_trades": metrics.total_trades >= settings.min_promotion_trades,
            "min_win_rate": metrics.win_rate >= settings.min_promotion_win_rate,
            "min_profit_factor": metrics.profit_factor
            >= settings.min_promotion_profit_factor,
            "max_drawdown": metrics.max_drawdown_percent
            <= settings.max_promotion_drawdown_percent,
            "max_consecutive_losses": metrics.consecutive_losses
            <= settings.max_promotion_consecutive_losses,
        }
        approved = all(gates.values())
        reason = "approved"
        if not gates["allow_promotion"]:
            reason = "promotion_disabled_by_config"
        elif not gates["min_trades"]:
            reason = "insufficient_trades"
        elif not gates["min_win_rate"]:
            reason = "win_rate_below_threshold"
        elif not gates["min_profit_factor"]:
            reason = "profit_factor_below_threshold"
        elif not gates["max_drawdown"]:
            reason = "drawdown_above_threshold"
        elif not gates["max_consecutive_losses"]:
            reason = "consecutive_losses_above_threshold"

        return StrategyPromotionDecision(
            strategy=result.strategy,
            approved=approved,
            reason=reason,
            metrics=metrics,
            gates=gates,
            timestamp=datetime.now(timezone.utc),
        )
