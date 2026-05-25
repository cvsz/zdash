from app.iot.tapo_adapter import TapoAdapter


def test_tapo_power_cycle_dry_run_reason():
    adapter = TapoAdapter()
    result = adapter.power_cycle()
    assert result['ok'] is True
    assert result['dry_run'] is True
    assert result['reason'] in {'dry_run', 'confirmation_required'}
