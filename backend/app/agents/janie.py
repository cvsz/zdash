from __future__ import annotations

from typing import Any

from app.agents.base import AgentMessage, BaseAgent
from app.ai.base import AIAdapter


class JanieAgent(BaseAgent):
    def __init__(self, ai_adapter: AIAdapter) -> None:
        super().__init__(
            agent_id="janie",
            name="Sophia Lane",
            role="coordinator_manager",
            metadata={"tier": "epic", "legacy_name": "Janie"},
        )
        self.ai_adapter = ai_adapter

    def receive_message(self, message: AgentMessage) -> dict[str, Any]:
        self.emit_event(
            "agent.message.received",
            "Sophia Lane received message",
            message.model_dump(),
        )
        response = self.run_task(task=message.message, context=message.context)
        self.emit_event(
            "agent.message.sent",
            "Sophia Lane sent response",
            {"to_agent": message.from_agent, "response": response["response_text"]},
        )
        return response

    def run_task(
        self, task: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        self.status = "running"
        ai_result = self.ai_adapter.generate_response(prompt=task, context=context)
        self.emit_event(
            "ai.response.generated",
            "AI response generated",
            {"provider": ai_result.provider, "model": ai_result.model},
        )
        self.status = "idle"
        return {
            "agent": self.id,
            "response_text": ai_result.text,
            "provider": ai_result.provider,
            "model": ai_result.model,
            "metadata": ai_result.metadata,
        }
