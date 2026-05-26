from app.agents.registry import MessageRequest, bootstrap_agents
from app.api import agents, logs
from app.core.events import event_bus


def assert_envelope(payload: dict) -> None:
    assert set(payload.keys()) == {'ok', 'data', 'error', 'timestamp'}


def test_agents_are_registered() -> None:
    bootstrap_agents()
    body = agents.list_agents()
    assert_envelope(body)
    agent_rows = body['data']['agents']
    ids = {agent['id'] for agent in agent_rows}
    assert 'ceo' in ids
    assert 'janie' in ids


def test_event_logs_created() -> None:
    event_bus.clear()
    bootstrap_agents()
    msg_response = agents.send_message(
        MessageRequest(
            from_agent='ceo',
            to_agent='janie',
            message='Hello Janie, report status.',
            context={},
        )
    )
    assert msg_response['ok'] is True

    logs_body = logs.list_logs(limit=100)
    assert_envelope(logs_body)

    event_types = [event['type'] for event in logs_body['data']['events']]
    assert 'agent.message.sent' in event_types
    assert 'agent.message.received' in event_types
    assert 'ai.response.generated' in event_types
