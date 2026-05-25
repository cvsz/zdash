from fastapi.testclient import TestClient

from app.main import app
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
    with TestClient(app) as client:
        response = client.get('/api/risk/status')
    assert response.status_code == 200
    body = response.json()
    assert_envelope(body)
    assert 'guardian_enabled' in body['data']


def test_post_risk_check() -> None:
    reset_guardian_service()
    with TestClient(app) as client:
        response = client.post('/api/risk/check', json=_snapshot_payload())
    assert response.status_code == 200
    body = response.json()
    assert_envelope(body)
    assert 'decision' in body['data']


def test_post_halt_and_resume() -> None:
    reset_guardian_service()
    with TestClient(app) as client:
        halt_response = client.post('/api/risk/halt', json={'reason': 'Manual operator halt'})
        resume_response = client.post('/api/risk/resume', json={'reason': 'Reviewed and safe for dry-run resume'})

    assert halt_response.status_code == 200
    assert resume_response.status_code == 200
    assert halt_response.json()['data']['halt_state']['halted'] is True
    assert resume_response.json()['data']['halt_state']['halted'] is False


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
    with TestClient(app) as client:
        response = client.post('/api/risk/approve-execution', json=payload)

    assert response.status_code == 200
    body = response.json()
    assert_envelope(body)
    assert 'decision' in body['data']
