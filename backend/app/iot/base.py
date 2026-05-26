from __future__ import annotations

from abc import ABC, abstractmethod

from app.iot.models import IoTActionResult


class IoTAdapter(ABC):
    @abstractmethod
    def get_status(self, device_alias: str) -> IoTActionResult:
        raise NotImplementedError

    @abstractmethod
    def turn_on(self, device_alias: str) -> IoTActionResult:
        raise NotImplementedError

    @abstractmethod
    def turn_off(self, device_alias: str) -> IoTActionResult:
        raise NotImplementedError

    @abstractmethod
    def power_cycle(self, device_alias: str, confirmation: bool = False) -> IoTActionResult:
        raise NotImplementedError
