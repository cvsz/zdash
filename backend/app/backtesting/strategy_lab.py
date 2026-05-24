from __future__ import annotations

from collections import defaultdict

from app.backtesting.strategies import ob_aggressive, ob_conservative, trend_follow


STRATEGY_MAP = {
    'ob_aggressive': ob_aggressive.generate_signal,
    'ob_conservative': ob_conservative.generate_signal,
    'trend_follow': trend_follow.generate_signal,
}


class StrategyLab:
    def mock_prices(self, n: int = 200) -> list[float]:
        base = 2300.0
        return [base + (i * 0.15) + ((-1) ** i) * 0.4 for i in range(n)]

    def run(self, strategy_name: str, risk_per_trade: float = 1.0) -> dict:
        fn = STRATEGY_MAP[strategy_name]
        prices = self.mock_prices()
        pnl = 0.0
        wins = 0
        losses = 0
        consec_losses = 0
        max_consec_losses = 0
        monthly = defaultdict(float)
        equity = [10000.0]

        for i, price in enumerate(prices):
            signal = fn(price, i)
            if signal == 0:
                continue
            trade_pnl = (0.5 if (i % 2 == 0) else -0.35) * signal * risk_per_trade
            pnl += trade_pnl
            eq = equity[-1] + trade_pnl
            equity.append(eq)

            month_key = f'2026-{((i // 20) % 12) + 1:02d}'
            monthly[month_key] += trade_pnl

            if trade_pnl > 0:
                wins += 1
                consec_losses = 0
            else:
                losses += 1
                consec_losses += 1
                max_consec_losses = max(max_consec_losses, consec_losses)

        trades = wins + losses
        gross_profit = wins * 0.5
        gross_loss = losses * 0.35
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 9.9
        win_rate = (wins / trades * 100) if trades else 0

        peak = equity[0]
        max_dd = 0.0
        for value in equity:
            peak = max(peak, value)
            dd = ((peak - value) / peak) * 100
            max_dd = max(max_dd, dd)

        expectancy = pnl / trades if trades else 0

        return {
            'strategy': strategy_name,
            'win_rate': round(win_rate, 3),
            'profit_factor': round(profit_factor, 3),
            'max_drawdown': round(max_dd, 3),
            'average_rr': 1.4,
            'total_trades': trades,
            'expectancy': round(expectancy, 4),
            'sharpe_like_score': round((expectancy / 0.5) if expectancy else 0, 4),
            'consecutive_losses': max_consec_losses,
            'monthly_return_table': dict(monthly),
            'net_pnl': round(pnl, 4),
        }
