from app.core.config import get_settings


class KillSwitch:
    def __init__(self) -> None:
        settings = get_settings()
        self.emergency_threshold = settings.emergency_kill_switch_drawdown_percent
        self.soft_thresholds = [5.0, 10.0, 20.0]

    def check(self, drawdown_percent: float) -> dict:
        emergency = drawdown_percent >= self.emergency_threshold
        soft_hits = [t for t in self.soft_thresholds if drawdown_percent >= t]
        return {
            'emergency_triggered': emergency,
            'soft_threshold_hits': soft_hits,
            'drawdown_percent': drawdown_percent,
        }
