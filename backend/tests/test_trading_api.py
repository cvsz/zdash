from app.api import trading
from app.trading.models import ExecutionRequest, TradingSignal


def _assert_envelope(payload: dict) -> None:
    assert set(payload.keys()) == {'ok', 'data', 'error', 'timestamp'}


def _signal() -> TradingSignal:
    return TradingSignal(
        symbol='XAUUSD',
        timeframe='M5',
        direction='buy',
        strategy='ob_aggressive',
        confidence=0.71,
        entry=2300.0,
        stop_loss=2298.0,
        take_profit=2304.0,
        reason='api test',
    )


def test_get_trading_status() -> None:
    body = trading.trading_status()
    _assert_envelope(body)
    assert body['ok'] is True
    assert 'dry_run' in body['data']


def test_post_scan() -> None:
    body = trading.scan(trading.ScanRequest(symbol='XAUUSD', timeframe='M5'))
    _assert_envelope(body)
    assert body['ok'] is True
    assert body['data']['symbol'] == 'XAUUSD'
    assert 'latest_signal' in body['data']


def test_post_validate_signal() -> None:
    body = trading.validate_signal(_signal())
    _assert_envelope(body)
    assert body['ok'] is True
    assert 'valid' in body['data']


def test_post_dry_run_execute() -> None:
    request = ExecutionRequest(signal=_signal(), dry_run=True, confirmation=False)
    body = trading.dry_run_execute(request)
    _assert_envelope(body)
    assert body['ok'] is True
    assert body['data']['status'] == 'simulated'
