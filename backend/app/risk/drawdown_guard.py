from __future__ import annotations

from app.core.config import get_settings
from app.risk.models import AccountSnapshot, DrawdownResult


class DrawdownGuard:
    def __init__(self) -> None:
        self.settings = get_settings()

    @staticmethod
    def calculate_total_drawdown(snapshot: AccountSnapshot) -> float:
        if snapshot.peak_equity <= 0:
            return 0.0
        drawdown = (
            (snapshot.peak_equity - snapshot.equity) / snapshot.peak_equity
        ) * 100.0
        return round(max(drawdown, 0.0), 4)

    @staticmethod
    def calculate_daily_drawdown(snapshot: AccountSnapshot) -> float:
        if snapshot.daily_start_equity <= 0:
            return 0.0
        drawdown = (
            (snapshot.daily_start_equity - snapshot.equity)
            / snapshot.daily_start_equity
        ) * 100.0
        return round(max(drawdown, 0.0), 4)

    def evaluate(self, snapshot: AccountSnapshot) -> DrawdownResult:
        total_dd = self.calculate_total_drawdown(snapshot)
        daily_dd = self.calculate_daily_drawdown(snapshot)

        if snapshot.peak_equity <= 0 or snapshot.daily_start_equity <= 0:
            return DrawdownResult(
                current_equity=snapshot.equity,
                peak_equity=snapshot.peak_equity,
                daily_start_equity=snapshot.daily_start_equity,
                total_drawdown_percent=total_dd,
                daily_drawdown_percent=daily_dd,
                floating_pnl=snapshot.floating_pnl,
                risk_level="warning",
                breached=False,
                breach_reason="Invalid peak/daily baseline equity. Drawdown treated as safe fallback.",
            )

        soft1 = self.settings.soft_halt_drawdown_level_1
        soft2 = self.settings.soft_halt_drawdown_level_2
        soft3 = self.settings.soft_halt_drawdown_level_3

        max_daily = self.settings.max_daily_drawdown_percent
        max_total = self.settings.max_total_drawdown_percent
        emergency = self.settings.emergency_kill_switch_drawdown_percent

        risk_level = "normal"
        breached = False
        breach_reason: str | None = None

        if total_dd >= emergency:
            risk_level = "emergency"
            breached = True
            breach_reason = f"Emergency threshold breached: total_drawdown={total_dd}% >= {emergency}%"
        elif total_dd >= max_total or daily_dd >= max_daily:
            risk_level = "danger"
            breached = True
            breach_reason = f"Max drawdown breached: total={total_dd}%/{max_total}% daily={daily_dd}%/{max_daily}%"
        else:
            max_observed = max(total_dd, daily_dd)
            if max_observed >= soft3:
                risk_level = "danger"
            elif max_observed >= soft2 or max_observed >= soft1:
                risk_level = "warning"

        return DrawdownResult(
            current_equity=snapshot.equity,
            peak_equity=snapshot.peak_equity,
            daily_start_equity=snapshot.daily_start_equity,
            total_drawdown_percent=total_dd,
            daily_drawdown_percent=daily_dd,
            floating_pnl=snapshot.floating_pnl,
            risk_level=risk_level,
            breached=breached,
            breach_reason=breach_reason,
        )
