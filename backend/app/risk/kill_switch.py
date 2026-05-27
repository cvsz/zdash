from __future__ import annotations

from app.core.config import get_settings
from app.core.events import event_bus
from app.risk.halt_flag import HaltFlagStore
from app.risk.models import DrawdownResult, HaltState


class KillSwitch:
    def __init__(self) -> None:
        self.settings = get_settings()

    def should_trigger(self, drawdown: DrawdownResult) -> bool:
        if (
            drawdown.total_drawdown_percent
            >= self.settings.emergency_kill_switch_drawdown_percent
        ):
            return True
        if (
            self.settings.hard_halt_on_daily_drawdown
            and drawdown.daily_drawdown_percent
            >= self.settings.max_daily_drawdown_percent
        ):
            return True
        return False

    def trigger(self, drawdown: DrawdownResult, halt_store: HaltFlagStore) -> HaltState:
        reason = (
            "Emergency stop triggered "
            f"(risk_level={drawdown.risk_level}, "
            f"total_drawdown={drawdown.total_drawdown_percent}%, "
            f"daily_drawdown={drawdown.daily_drawdown_percent}%)"
        )
        state = halt_store.halt(reason=reason, source="kill_switch")
        event_bus.emit(
            "risk.emergency_stop.triggered",
            "KillSwitch",
            "Emergency stop triggered by drawdown guard",
            {
                "risk_level": drawdown.risk_level,
                "total_drawdown_percent": drawdown.total_drawdown_percent,
                "daily_drawdown_percent": drawdown.daily_drawdown_percent,
            },
        )
        return state
