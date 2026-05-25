from app.core.config import get_settings
from app.iot.tapo_adapter import TapoAdapter


class IoTService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.adapter = TapoAdapter()

    def power_cycle(self, confirmation: bool = False) -> dict:
        if not self.settings.iot_enabled:
            return {'ok': False, 'reason': 'iot_disabled', 'dry_run': self.settings.iot_dry_run}
        return self.adapter.power_cycle(confirmation=confirmation)
