from __future__ import annotations

from typing import Any

from app.agents.base import AgentMessage, BaseAgent


class CEOAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_id='ceo', name='CEO', role='commander')

    def receive_message(self, message: AgentMessage) -> dict[str, Any]:
        self.emit_event('agent.message.received', 'CEO received message', message.model_dump())
        return {'acknowledged': True, 'agent': self.id}

    def run_task(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        self.status = 'running'
        self.emit_event('agent.message.sent', 'CEO ran task', {'task': task, 'context': context or {}})
        self.status = 'idle'
        return {'agent': self.id, 'task': task, 'result': 'completed'}

    def create_message(self, to_agent: str, message: str, context: dict[str, Any] | None = None) -> AgentMessage:
        return AgentMessage(from_agent=self.id, to_agent=to_agent, message=message, context=context or {})
