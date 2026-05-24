from fastapi.testclient import TestClient

from app.main import app


def assert_envelope(payload: dict) -> None:
    assert set(payload.keys()) == {'ok', 'data', 'error', 'timestamp'}


def test_health_endpoint_works() -> None:
    with TestClient(app) as client:
        response = client.get('/health')
    assert response.status_code == 200
    body = response.json()
    assert_envelope(body)
    assert body['ok'] is True
    assert body['error'] is None
    assert body['data']['status'] == 'ok'
    assert 'app_name' in body['data']
