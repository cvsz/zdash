from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from statistics import mean, pstdev

from app.backtesting.models import BacktestMetrics, SimulatedTrade


class BacktestMetricsCalculator:
    def calculate(
        self,
        trades: list[SimulatedTrade],
        initial_balance: float,
        final_balance: float,
        equity_curve: list[tuple[datetime, float]],
    ) -> BacktestMetrics:
        closed = [trade for trade in trades if trade.status == "closed"]
        wins = [t for t in closed if t.pnl > 0]
        losses = [t for t in closed if t.pnl < 0]
        gross_profit = sum(t.pnl for t in wins)
        gross_loss = abs(sum(t.pnl for t in losses))
        total = len(closed)
        win_rate = (len(wins) / total * 100.0) if total else 0.0
        if gross_loss > 0:
            profit_factor = gross_profit / gross_loss
        else:
            profit_factor = gross_profit if gross_profit > 0 else 0.0

        returns = [t.pnl_percent for t in closed]
        sharpe = 0.0
        if returns:
            variance = pstdev(returns)
            sharpe = (mean(returns) / variance) if variance > 0 else mean(returns)

        streak = 0
        current_streak = 0
        for t in closed:
            if t.pnl < 0:
                current_streak += 1
                streak = max(streak, current_streak)
            else:
                current_streak = 0

        monthly: defaultdict[str, float] = defaultdict(float)
        for t in closed:
            ts = t.exit_time or t.entry_time
            monthly[ts.strftime("%Y-%m")] += t.pnl

        peak = equity_curve[0][1] if equity_curve else initial_balance
        max_dd = 0.0
        for _, eq in equity_curve:
            peak = max(peak, eq)
            if peak > 0:
                max_dd = max(max_dd, ((peak - eq) / peak) * 100.0)

        net = final_balance - initial_balance
        return BacktestMetrics(
            total_trades=total,
            winning_trades=len(wins),
            losing_trades=len(losses),
            win_rate=round(win_rate, 4),
            gross_profit=round(gross_profit, 4),
            gross_loss=round(gross_loss, 4),
            net_profit=round(net, 4),
            net_profit_percent=round((net / initial_balance * 100.0) if initial_balance else 0.0, 4),
            profit_factor=round(profit_factor, 4),
            max_drawdown_percent=round(max_dd, 4),
            average_rr=round(sum(t.rr for t in closed) / total if total else 0.0, 4),
            expectancy=round(sum(t.pnl for t in closed) / total if total else 0.0, 4),
            sharpe_like_score=round(sharpe, 4),
            consecutive_losses=streak,
            monthly_return_table={k: round(v, 4) for k, v in monthly.items()},
        )
