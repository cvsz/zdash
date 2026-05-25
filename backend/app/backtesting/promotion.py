from __future__ import annotations

from datetime import datetime, timezone

from app.backtesting.models import BacktestResult, StrategyPromotionDecision
from app.core.config import get_settings


class StrategyPromotionGate:
    def evaluate(self, result: BacktestResult) -> StrategyPromotionDecision:
        s = get_settings()
        m = result.metrics
        gates = {
            "allow_promotion": s.allow_strategy_promotion,
            "min_trades": m.total_trades >= s.min_promotion_trades,
            "min_win_rate": m.win_rate >= s.min_promotion_win_rate,
            "min_profit_factor": m.profit_factor >= s.min_promotion_profit_factor,
            "max_drawdown": m.max_drawdown_percent <= s.max_promotion_drawdown_percent,
            "max_consecutive_losses": m.consecutive_losses <= s.max_promotion_consecutive_losses,
        }
        approved = all(gates.values())
        return StrategyPromotionDecision(strategy=result.strategy, approved=approved, reason="approved" if approved else "gates_not_satisfied", metrics=m, gates=gates, timestamp=datetime.now(timezone.utc))
