from fastapi import APIRouter

from app.agents.registry import MessageRequest, bootstrap_agents, registry
from app.core.config import get_settings
from app.core.responses import fail, ok

router = APIRouter(prefix="/api/agents", tags=["agents"])


def _trading_specialist_health() -> dict:
    settings = get_settings()
    return {
        "id": "trading",
        "name": "Damien Cross",
        "role": "Trading Specialist",
        "status": "idle" if settings.trading_enabled else "disabled",
        "metadata": {
            "stable_id": "trading",
            "module": "strategy",
            "dry_run": settings.dry_run,
            "default_symbol": settings.trading_symbol,
            "default_timeframe": settings.trading_timeframe,
        },
    }


@router.get("")
def list_agents() -> dict:
    bootstrap_agents()
    agents = [agent.health_check() for agent in registry.list()]
    if not any(agent.get("id") == "trading" for agent in agents):
        agents.append(_trading_specialist_health())
    return ok({"agents": agents})


@router.post("/message")
def send_message(payload: MessageRequest) -> dict:
    try:
        result = registry.send_message(payload)
    except ValueError as exc:
        return fail("AGENT_NOT_FOUND", str(exc))
    except Exception as exc:  # pragma: no cover
        return fail("MESSAGE_FLOW_ERROR", str(exc))
    return ok(result)
