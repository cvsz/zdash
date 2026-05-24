from abc import ABC, abstractmethod

from app.core.config import get_settings
from app.core.events import event_bus


class TapoAdapterBase(ABC):
    @abstractmethod
    def power_cycle(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def connectivity_test(self) -> dict:
        raise NotImplementedError


class TapoAdapter(TapoAdapterBase):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.allowed_actions = {'power_cycle'}

    def connectivity_test(self) -> dict:
        return {
            'configured': bool(self.settings.tapo_username and self.settings.tapo_password and self.settings.tapo_device_ip),
            'device_ip': self.settings.tapo_device_ip or 'not-configured',
            'dry_run': self.settings.iot_dry_run,
        }

    def power_cycle(self) -> dict:
        payload = {
            'action': 'power_cycle',
            'device_ip': self.settings.tapo_device_ip or 'not-configured',
            'dry_run': self.settings.iot_dry_run,
            'allowed': 'power_cycle' in self.allowed_actions,
        }
        event_bus.emit('iot_action', 'TapoAdapter', payload)
        return {'ok': True, **payload}
