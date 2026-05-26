from app.core.config import get_settings
from app.core.events import event_bus
from app.iot.iot_service import IoTService
from app.iot.models import IoTAction


def test_status_returns_dry_run_result() -> None:
    service = IoTService()
    result = service.get_status()
    assert result.ok is True
    assert result.dry_run is True


def test_power_cycle_simulates_in_dry_run() -> None:
    service = IoTService()
    result = service.power_cycle('zdash-power-node', confirmation=False)
    assert result.ok is True
    assert result.dry_run is True


def test_real_action_blocked_without_confirmation(monkeypatch) -> None:
    monkeypatch.setenv('IOT_ENABLED', 'true')
    monkeypatch.setenv('IOT_DRY_RUN', 'false')
    monkeypatch.setenv('IOT_REQUIRE_CONFIRMATION', 'true')
    get_settings.cache_clear()

    service = IoTService()
    result = service.execute(IoTAction(device_alias='zdash-power-node', action='power_cycle', confirmation=False))

    assert result.ok is False
    assert 'confirmation' in result.message.lower()


def test_disabled_iot_blocks_action(monkeypatch) -> None:
    monkeypatch.setenv('IOT_ENABLED', 'false')
    get_settings.cache_clear()

    service = IoTService()
    result = service.execute(IoTAction(device_alias='zdash-power-node', action='power_cycle', confirmation=True))

    assert result.ok is False
    assert 'disabled' in result.message.lower()


def test_iot_events_are_emitted() -> None:
    service = IoTService()
    event_bus.clear()

    service.execute(IoTAction(device_alias='zdash-power-node', action='power_cycle', confirmation=False))

    types = [event.type for event in event_bus.list_events(limit=20)]
    assert 'iot.action.requested' in types
    assert 'iot.action.simulated' in types
