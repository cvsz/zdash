from __future__ import annotations

from typing import Any

from app.agents.base import AgentMessage, BaseAgent
from app.content.models import (
    ApproveContentRequest,
    PublishContentRequest,
    ScheduleContentRequest,
)
from app.content.pipeline import ContentPipeline, get_content_pipeline
from app.core.events import event_bus


class SocialAgent(BaseAgent):
    def __init__(self, pipeline: ContentPipeline | None = None) -> None:
        super().__init__(
            agent_id="social",
            name="Maya Quinn",
            role="social_media_specialist",
            metadata={"tier": "epic", "legacy_name": "Social"},
        )
        self.pipeline = pipeline or get_content_pipeline()

    def receive_message(self, message: AgentMessage) -> dict[str, Any]:
        self._emit_received("receive_message", {"message": message.message})
        result = self.run_task(task=message.message, context=message.context)
        return {"from": self.id, "to": message.from_agent, "response": result}

    def run_task(
        self, task: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        ctx = context or {}
        if task == "health_check":
            result: dict[str, Any] = self.health_check()
        elif task == "schedule_content":
            schedule_request = ScheduleContentRequest.model_validate(
                ctx.get("request", ctx)
            )
            item = self.schedule_content(schedule_request)
            result = {"item": item.model_dump(mode="json")}
        elif task == "approve_content":
            approve_request = ApproveContentRequest.model_validate(
                ctx.get("request", ctx)
            )
            item = self.approve_content(approve_request)
            result = {"item": item.model_dump(mode="json")}
        elif task == "publish_content":
            publish_request = PublishContentRequest.model_validate(
                ctx.get("request", ctx)
            )
            post_results = self.publish_content(publish_request)
            result = {"results": [entry.model_dump(mode="json") for entry in post_results]}
        else:
            raise ValueError(f"Unsupported social task: {task}")
        return {"task": task, "ok": True, **result}

    def schedule_content(self, request: ScheduleContentRequest):
        self._emit_received("schedule_content")
        self.status = "running"
        try:
            item = self.pipeline.social.schedule_content(request)
            self.status = "idle"
            self._emit_completed("schedule_content", {"content_id": item.id})
            return item
        except Exception as exc:
            self.status = "error"
            self._emit_failed("schedule_content", exc)
            raise

    def approve_content(self, request: ApproveContentRequest):
        self._emit_received("approve_content")
        self.status = "running"
        try:
            item = self.pipeline.social.approve_content(request)
            self.status = "idle"
            self._emit_completed("approve_content", {"content_id": item.id})
            return item
        except Exception as exc:
            self.status = "error"
            self._emit_failed("approve_content", exc)
            raise

    def publish_content(self, request: PublishContentRequest):
        self._emit_received("publish_content")
        self.status = "running"
        try:
            results = self.pipeline.social.publish_content(request)
            self.status = "idle"
            self._emit_completed(
                "publish_content",
                {"content_id": request.content_id, "result_count": len(results)},
            )
            return results
        except Exception as exc:
            self.status = "error"
            self._emit_failed("publish_content", exc)
            raise

    def health_check(self) -> dict[str, Any]:
        base = super().health_check()
        base["pipeline"] = self.pipeline.get_status()
        return base

    def _emit_received(
        self, command: str, payload: dict[str, Any] | None = None
    ) -> None:
        event_bus.emit(
            "social.command.received",
            self.id,
            "Social command received",
            {"command": command, **(payload or {})},
        )

    def _emit_completed(
        self, command: str, payload: dict[str, Any] | None = None
    ) -> None:
        event_bus.emit(
            "social.command.completed",
            self.id,
            "Social command completed",
            {"command": command, **(payload or {})},
        )

    def _emit_failed(self, command: str, exc: Exception) -> None:
        event_bus.emit(
            "social.command.failed",
            self.id,
            "Social command failed",
            {"command": command, "error": str(exc)},
        )
