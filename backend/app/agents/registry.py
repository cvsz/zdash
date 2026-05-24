from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.agents.base import AgentMessage, BaseAgent
from app.agents.ceo import CEOAgent
from app.agents.janie import JanieAgent
from app.ai.claude_adapter import ClaudeAdapter
from app.ai.mock_adapter import MockAIAdapter
from app.core.config import get_settings
from app.core.events import Event, event_bus


class MessageRequest(BaseModel):
    from_agent: str
    to_agent: str
    message: str
    context: dict[str, Any] = Field(default_factory=dict)


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.id] = agent

    def get(self, agent_id: str) -> BaseAgent | None:
        return self._agents.get(agent_id)

    def list(self) -> list[BaseAgent]:
        return list(self._agents.values())

    def send_message(self, request: MessageRequest) -> dict[str, Any]:
        from_agent = self.get(request.from_agent)
        to_agent = self.get(request.to_agent)

        if from_agent is None:
            raise ValueError(f"Unknown source agent: {request.from_agent}")
        if to_agent is None:
            raise ValueError(f"Unknown target agent: {request.to_agent}")

        msg_id = str(uuid4())
        envelope = AgentMessage(
            from_agent=request.from_agent,
            to_agent=request.to_agent,
            message=request.message,
            context=request.context,
        )

        sent_event = event_bus.emit(
            event_type='agent.message.sent',
            source=request.from_agent,
            message='Message dispatched',
            payload={'message_id': msg_id, **envelope.model_dump()},
        )

        response = to_agent.receive_message(envelope)

        related_events = _find_related_events(msg_id=msg_id, base_event=sent_event)
        return {
            'message_id': msg_id,
            'from_agent': request.from_agent,
            'to_agent': request.to_agent,
            'response_text': response['response_text'],
            'event_ids': [event.id for event in related_events],
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }


def _find_related_events(msg_id: str, base_event: Event) -> list[Event]:
    events = event_bus.list_events(limit=20)
    related: list[Event] = [base_event]
    for event in events:
        payload = event.payload if isinstance(event.payload, dict) else {}
        if payload.get('message_id') == msg_id:
            related.append(event)
    unique: dict[str, Event] = {event.id: event for event in related}
    return list(unique.values())


def build_default_ai_adapter():
    settings = get_settings()
    if settings.ai_provider.lower() == 'claude':
        return ClaudeAdapter()
    return MockAIAdapter()


registry = AgentRegistry()


def bootstrap_agents() -> None:
    if registry.get('ceo') and registry.get('janie'):
        return

    ceo = CEOAgent()
    janie = JanieAgent(ai_adapter=build_default_ai_adapter())

    registry.register(ceo)
    registry.register(janie)

    event_bus.emit('system.startup', 'system', 'Janie runtime bootstrapped', {'agents': ['ceo', 'janie']})
