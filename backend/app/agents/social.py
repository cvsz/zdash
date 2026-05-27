from typing import Any

from app.agents.base import AgentMessage, BaseAgent
from app.content.models import (
    ApproveContentRequest,
    PublishContentRequest,
    ScheduleContentRequest,
)
from app.content.pipeline import content_pipeline
from app.core.events import event_bus


class SocialAgent(BaseAgent):
    id = "social"
    name = "Maya Quinn"
    role = "social_media_specialist"

    def __init__(self) -> None:
        super().__init__(
            agent_id=self.id,
            name=self.name,
            role=self.role,
            metadata={"tier": "epic", "legacy_name": "Social"},
        )

    def receive_message(self, message: AgentMessage) -> dict[str, Any]:
        self.emit_event(
            "agent.message.received",
            "Maya Quinn received message",
            {"from_agent": message.from_agent, "message": message.message},
        )
        return {"response_text": "Maya Quinn is ready.", "agent": self.id}

    def run_task(
        self, task: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        self.emit_event(
            "agent.task.run",
            "Maya Quinn task requested",
            {"task": task, "context": context or {}},
        )
        return {"ok": True, "agent": self.id, "task": task, "dry_run": True}

    def schedule_content(self, request: ScheduleContentRequest):
        event_bus.emit("social.command.received", self.id, "schedule_content", {})
        item = content_pipeline.social.schedule_content(request)
        event_bus.emit(
            "social.command.completed",
            self.id,
            "schedule_content",
            {"content_id": item.id},
        )
        return item

    def approve_content(self, request: ApproveContentRequest):
        item = content_pipeline.social.approve_content(request)
        return item

    def publish_content(self, request: PublishContentRequest):
        return content_pipeline.social.publish_content(request)
