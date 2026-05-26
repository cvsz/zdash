from __future__ import annotations

from app.core.config import get_settings
from app.core.events import event_bus
from app.iot.models import IoTAction, IoTActionResult
from app.iot.tapo_adapter import TapoAdapter


class IoTService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.adapter = TapoAdapter()

    def get_status(self, device_alias: str | None = None) -> IoTActionResult:
        alias = device_alias or self.settings.tapo_device_alias
        event_bus.emit('iot.action.requested', 'IoTService', 'IoT status requested', {'device_alias': alias})
        try:
            result = self.adapter.get_status(alias)
        except Exception as exc:
            event_bus.emit('iot.action.failed', 'IoTService', 'IoT status failed', {'device_alias': alias, 'error': str(exc)})
            raise

        if result.dry_run:
            event_bus.emit('iot.action.simulated', 'IoTService', 'IoT status simulated', result.model_dump(mode='json'))
        else:
            event_bus.emit('iot.action.completed', 'IoTService', 'IoT status completed', result.model_dump(mode='json'))
        return result

    def execute(self, action: IoTAction) -> IoTActionResult:
        event_bus.emit('iot.action.requested', 'IoTService', 'IoT action requested', action.model_dump(mode='json'))

        if action.action != 'status' and not self.settings.iot_enabled:
            result = self._blocked(action, 'IoT is disabled by configuration.', reason='iot_disabled')
            event_bus.emit('iot.action.blocked', 'IoTService', 'IoT action blocked', result.model_dump(mode='json'))
            return result

        if action.action != 'status' and not self.settings.iot_dry_run and self.settings.iot_require_confirmation and not action.confirmation:
            result = self._blocked(action, 'IoT action blocked: confirmation required.', reason='confirmation_required')
            event_bus.emit('iot.action.blocked', 'IoTService', 'IoT action blocked', result.model_dump(mode='json'))
            return result

        try:
            if action.action == 'status':
                result = self.adapter.get_status(action.device_alias)
            elif action.action == 'turn_on':
                result = self.adapter.turn_on(action.device_alias)
            elif action.action == 'turn_off':
                result = self.adapter.turn_off(action.device_alias)
            elif action.action == 'power_cycle':
                result = self.adapter.power_cycle(action.device_alias, confirmation=action.confirmation)
            else:
                result = self._blocked(action, f'Unsupported IoT action: {action.action}', reason='unsupported_action')
        except Exception as exc:
            event_bus.emit('iot.action.failed', 'IoTService', 'IoT action failed', {'error': str(exc), 'action': action.action})
            raise

        if result.ok:
            event_type = 'iot.action.simulated' if result.dry_run else 'iot.action.completed'
            event_bus.emit(event_type, 'IoTService', 'IoT action completed', result.model_dump(mode='json'))
        else:
            lowered = result.message.lower()
            event_type = 'iot.action.blocked' if 'blocked' in lowered or 'required' in lowered else 'iot.action.failed'
            event_bus.emit(event_type, 'IoTService', 'IoT action did not complete', result.model_dump(mode='json'))

        return result

    def turn_on(self, device_alias: str, confirmation: bool = False) -> IoTActionResult:
        return self.execute(IoTAction(device_alias=device_alias, action='turn_on', confirmation=confirmation))

    def turn_off(self, device_alias: str, confirmation: bool = False) -> IoTActionResult:
        return self.execute(IoTAction(device_alias=device_alias, action='turn_off', confirmation=confirmation))

    def power_cycle(self, device_alias: str, confirmation: bool = False) -> IoTActionResult:
        return self.execute(IoTAction(device_alias=device_alias, action='power_cycle', confirmation=confirmation))

    def _blocked(self, action: IoTAction, message: str, reason: str) -> IoTActionResult:
        return IoTActionResult(
            ok=False,
            dry_run=bool(self.settings.iot_dry_run),
            device_alias=action.device_alias,
            action=action.action,
            message=message,
            output={'reason': reason, 'blocked': True},
        )
