from dataclasses import dataclass


@dataclass
class EquitySnapshot:
    start_balance: float
    current_balance: float
    peak_balance: float


class DrawdownGuard:
    @staticmethod
    def percent_drawdown(peak: float, current: float) -> float:
        if peak <= 0:
            return 0.0
        return ((peak - current) / peak) * 100.0

    def evaluate(self, snapshot: EquitySnapshot) -> dict[str, float]:
        total_dd = self.percent_drawdown(snapshot.peak_balance, snapshot.current_balance)
        daily_dd = self.percent_drawdown(snapshot.start_balance, snapshot.current_balance)
        return {'daily_drawdown_percent': round(daily_dd, 4), 'total_drawdown_percent': round(total_dd, 4)}
