from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from statistics import pstdev

from app.backtesting.models import BacktestMetrics, SimulatedTrade


class BacktestMetricsCalculator:
    def calculate(self, trades: list[SimulatedTrade], initial_balance: float, final_balance: float, equity_curve: list[tuple[datetime, float]]) -> BacktestMetrics:
        closed = [t for t in trades if t.status == "closed"]
        wins = [t for t in closed if t.pnl > 0]
        losses = [t for t in closed if t.pnl < 0]
        gross_profit = sum(t.pnl for t in wins)
        gross_loss = abs(sum(t.pnl for t in losses))
        total = len(closed)
        win_rate = (len(wins) / total * 100) if total else 0
        pf = (gross_profit / gross_loss) if gross_loss else (999.0 if gross_profit > 0 else 0)
        returns = [t.pnl_percent for t in closed]
        sharpe = (sum(returns) / len(returns) / (pstdev(returns) or 1)) if returns else 0
        streak = cur = 0
        for t in closed:
            if t.pnl < 0:
                cur += 1
                streak = max(streak, cur)
            else:
                cur = 0
        monthly = defaultdict(float)
        for t in closed:
            monthly[t.entry_time.strftime("%Y-%m")] += t.pnl
        peak = equity_curve[0][1] if equity_curve else initial_balance
        max_dd = 0.0
        for _, eq in equity_curve:
            peak = max(peak, eq)
            max_dd = max(max_dd, ((peak - eq) / peak) * 100 if peak else 0)
        net = final_balance - initial_balance
        return BacktestMetrics(
            total_trades=total,
            winning_trades=len(wins),
            losing_trades=len(losses),
            win_rate=round(win_rate, 4),
            gross_profit=round(gross_profit, 4),
            gross_loss=round(gross_loss, 4),
            net_profit=round(net, 4),
            net_profit_percent=round((net / initial_balance * 100) if initial_balance else 0, 4),
            profit_factor=round(pf, 4),
            max_drawdown_percent=round(max_dd, 4),
            average_rr=round(sum(t.rr for t in closed) / total if total else 0, 4),
            expectancy=round(sum(t.pnl for t in closed) / total if total else 0, 4),
            sharpe_like_score=round(sharpe, 4),
            consecutive_losses=streak,
            monthly_return_table={k: round(v, 4) for k, v in monthly.items()},
        )
