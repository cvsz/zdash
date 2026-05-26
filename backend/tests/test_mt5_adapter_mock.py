from app.core.config import get_settings
from app.trading.mt5_adapter import MT5Adapter


def test_mt5_mock_mode_when_disabled(monkeypatch) -> None:
    monkeypatch.setenv('MT5_ENABLED', 'false')
    get_settings.cache_clear()

    adapter = MT5Adapter()
    status = adapter.connect()

    assert status['mode'] == 'mock'
    assert status['connected'] is False

    get_settings.cache_clear()


def test_missing_mt5_package_does_not_crash(monkeypatch) -> None:
    monkeypatch.setenv('MT5_ENABLED', 'true')
    monkeypatch.setenv('MT5_LOGIN', '1')
    monkeypatch.setenv('MT5_PASSWORD', 'x')
    monkeypatch.setenv('MT5_SERVER', 'demo')
    get_settings.cache_clear()

    adapter = MT5Adapter()
    adapter._mt5_module = None
    status = adapter.connect()

    assert status['mode'] == 'mock'
    assert status['connected'] is False

    get_settings.cache_clear()


def test_mock_candles_are_returned() -> None:
    adapter = MT5Adapter()
    candles = adapter.get_candles(symbol='XAUUSD', timeframe='M5', limit=300)

    assert len(candles) >= 300
    assert candles[0].close > 0
