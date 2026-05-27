from app.core.config import get_settings
from app.iot.tapo_adapter import TapoAdapter


def test_missing_credentials_do_not_crash(monkeypatch) -> None:
    monkeypatch.setenv("IOT_DRY_RUN", "false")
    monkeypatch.delenv("TAPO_USERNAME", raising=False)
    monkeypatch.delenv("TAPO_PASSWORD", raising=False)
    monkeypatch.delenv("TAPO_DEVICE_IP", raising=False)
    get_settings.cache_clear()

    adapter = TapoAdapter()
    result = adapter.power_cycle(device_alias="zdash-power-node", confirmation=True)

    assert result.ok is True
    assert result.dry_run is True
    assert "simulation" in result.message.lower()


def test_dry_run_turn_on_returns_simulated() -> None:
    adapter = TapoAdapter()
    result = adapter.turn_on("zdash-power-node")
    assert result.ok is True
    assert result.dry_run is True
    assert "simulated" in result.message.lower()


def test_dry_run_turn_off_returns_simulated() -> None:
    adapter = TapoAdapter()
    result = adapter.turn_off("zdash-power-node")
    assert result.ok is True
    assert result.dry_run is True
    assert "simulated" in result.message.lower()


def test_dry_run_power_cycle_returns_simulated() -> None:
    adapter = TapoAdapter()
    result = adapter.power_cycle(device_alias="zdash-power-node", confirmation=False)
    assert result.ok is True
    assert result.dry_run is True
    assert "simulated" in result.message.lower()
