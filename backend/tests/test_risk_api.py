from app.api import risk
from app.risk.models import AccountSnapshot
from app.risk.guardian_service import reset_guardian_service


def assert_envelope(payload: dict) -> None:
    assert set(payload.keys()) == {'ok', 'data', 'error', 'timestamp'}


def _snapshot_payload() -> dict:
    return {
        'balance': 10000,
        'equity': 9500,
        'peak_equity': 10000,
        'daily_start_equity': 10000,
        'open_positions': 0,
        'floating_pnl': -500,
        'realized_pnl_today': -500,
    }


def test_get_risk_status() -> None:
    reset_guardian_service()
    body = risk.status()
    assert_envelope(body)
    assert 'guardian_enabled' in body['data']


def test_post_risk_check() -> None:
    reset_guardian_service()
    body = risk.check(AccountSnapshot.model_validate(_snapshot_payload()))
    assert_envelope(body)
    assert 'decision' in body['data']


def test_post_halt_and_resume() -> None:
    reset_guardian_service()
    halt_response = risk.halt(risk.HaltRequest(reason='Manual operator halt'))
    resume_response = risk.resume(risk.HaltRequest(reason='Reviewed and safe for dry-run resume'))

    assert halt_response['ok'] is True
    assert resume_response['ok'] is True
    assert halt_response['data']['halt_state']['halted'] is True
    assert resume_response['data']['halt_state']['halted'] is False


def test_post_approve_execution() -> None:
    reset_guardian_service()
    payload = {
        'signal': {
            'symbol': 'XAUUSD',
            'timeframe': 'M5',
            'direction': 'buy',
            'strategy': 'ob_aggressive',
            'confidence': 0.72,
        },
        'snapshot': _snapshot_payload(),
    }
    body = risk.approve_execution(
        risk.ApproveExecutionRequest(
            signal=payload['signal'],
            snapshot=AccountSnapshot.model_validate(payload['snapshot']),
        )
    )
    assert_envelope(body)
    assert 'decision' in body['data']
