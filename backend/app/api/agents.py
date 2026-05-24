from fastapi import APIRouter

from app.agents.registry import MessageRequest, registry
from app.core.responses import fail, ok

router = APIRouter(prefix='/api/agents', tags=['agents'])


@router.get('')
def list_agents() -> dict:
    agents = [agent.health_check() for agent in registry.list()]
    return ok({'agents': agents})


@router.post('/message')
def send_message(payload: MessageRequest) -> dict:
    try:
        result = registry.send_message(payload)
    except ValueError as exc:
        return fail('AGENT_NOT_FOUND', str(exc))
    except Exception as exc:  # pragma: no cover
        return fail('MESSAGE_FLOW_ERROR', str(exc))
    return ok(result)
