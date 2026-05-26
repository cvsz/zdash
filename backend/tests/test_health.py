from app.api import health


def assert_envelope(payload: dict) -> None:
    assert set(payload.keys()) == {'ok', 'data', 'error', 'timestamp'}


def test_health_endpoint_works() -> None:
    body = health.health()
    assert_envelope(body)
    assert body['ok'] is True
    assert body['error'] is None
    assert body['data']['status'] == 'ok'
    assert 'app_name' in body['data']
