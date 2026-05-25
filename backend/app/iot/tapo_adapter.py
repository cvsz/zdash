from app.core.config import get_settings
from app.core.events import event_bus
from app.iot.base import IoTAdapterBase


class TapoAdapter(IoTAdapterBase):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.allowed_actions = {'power_cycle'}

    def connectivity_test(self) -> dict:
        return {
            'configured': bool(self.settings.tapo_username and self.settings.tapo_password and self.settings.tapo_device_ip),
            'device_ip': self.settings.tapo_device_ip or 'not-configured',
            'dry_run': self.settings.iot_dry_run,
        }

    def power_cycle(self, confirmation: bool = False) -> dict:
        payload = {
            'action': 'power_cycle',
            'device_ip': self.settings.tapo_device_ip or 'not-configured',
            'dry_run': self.settings.iot_dry_run,
            'allowed': 'power_cycle' in self.allowed_actions,
            'confirmation': confirmation,
        }
        if self.settings.iot_dry_run:
            payload['reason'] = 'dry_run'
        elif self.settings.iot_require_confirmation and not confirmation:
            payload['reason'] = 'confirmation_required'
            payload['allowed'] = False
        event_bus.emit('iot_action', 'TapoAdapter', payload)
        return {'ok': True, **payload}
