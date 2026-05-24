from fastapi.testclient import TestClient

from app.main import app


def assert_envelope(payload: dict) -> None:
    assert set(payload.keys()) == {'ok', 'data', 'error', 'timestamp'}


def test_agents_are_registered() -> None:
    with TestClient(app) as client:
        response = client.get('/api/agents')
    assert response.status_code == 200
    body = response.json()
    assert_envelope(body)
    agents = body['data']['agents']
    ids = {agent['id'] for agent in agents}
    assert 'ceo' in ids
    assert 'janie' in ids


def test_event_logs_created() -> None:
    with TestClient(app) as client:
        msg_response = client.post(
            '/api/agents/message',
            json={
                'from_agent': 'ceo',
                'to_agent': 'janie',
                'message': 'Hello Janie, report status.',
                'context': {},
            },
        )
        assert msg_response.status_code == 200

        logs_response = client.get('/api/logs')

    assert logs_response.status_code == 200
    logs_body = logs_response.json()
    assert_envelope(logs_body)

    event_types = [event['type'] for event in logs_body['data']['events']]
    assert 'agent.message.sent' in event_types
    assert 'agent.message.received' in event_types
    assert 'ai.response.generated' in event_types
