from typing import Any

from app.agents.base import AgentMessage, BaseAgent
from app.content.models import GraphicRequest
from app.content.pipeline import content_pipeline
from app.core.events import event_bus


class GraphicAgent(BaseAgent):
    id = "graphic"
    name = "Julian Reed"
    role = "design_specialist"

    def __init__(self) -> None:
        super().__init__(
            agent_id=self.id,
            name=self.name,
            role=self.role,
            metadata={"tier": "epic", "legacy_name": "Graphic"},
        )

    def receive_message(self, message: AgentMessage) -> dict[str, Any]:
        self.emit_event(
            "agent.message.received",
            "Julian Reed received message",
            {"from_agent": message.from_agent, "message": message.message},
        )
        return {"response_text": "Julian Reed is ready.", "agent": self.id}

    def run_task(
        self, task: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        self.emit_event(
            "agent.task.run",
            "Julian Reed task requested",
            {"task": task, "context": context or {}},
        )
        return {"ok": True, "agent": self.id, "task": task, "dry_run": True}

    def create_graphic_prompt(self, request: GraphicRequest):
        event_bus.emit("graphic.command.received", self.id, "create_graphic_prompt", {})
        item = content_pipeline.graphic.create_graphic_prompt(request)
        event_bus.emit(
            "graphic.command.completed",
            self.id,
            "create_graphic_prompt",
            {"content_id": item.id},
        )
        return item

    def generate_graphic(self, request: GraphicRequest):
        event_bus.emit("graphic.command.received", self.id, "generate_graphic", {})
        item = content_pipeline.graphic.generate_graphic(request)
        event_bus.emit(
            "graphic.command.completed",
            self.id,
            "generate_graphic",
            {"content_id": item.id},
        )
        return item
