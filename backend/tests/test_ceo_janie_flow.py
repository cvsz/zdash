from app.agents.registry import MessageRequest, bootstrap_agents
from app.api import agents


def assert_envelope(payload: dict) -> None:
    assert set(payload.keys()) == {'ok', 'data', 'error', 'timestamp'}


def test_ceo_can_send_message_to_janie() -> None:
    bootstrap_agents()
    body = agents.send_message(
        MessageRequest(
            from_agent='ceo',
            to_agent='janie',
            message='Hello Janie, report system status.',
            context={},
        )
    )
    assert_envelope(body)
    assert body['ok'] is True

    data = body['data']
    assert data['from_agent'] == 'ceo'
    assert data['to_agent'] == 'janie'
    assert data['message_id']
    assert isinstance(data['event_ids'], list)
    assert len(data['event_ids']) >= 1
    assert '[MOCK] Janie received:' in data['response_text']
