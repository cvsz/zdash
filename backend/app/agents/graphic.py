from __future__ import annotations

from typing import Any

from app.agents.base import AgentMessage, BaseAgent
from app.content.models import GraphicRequest
from app.content.pipeline import ContentPipeline, get_content_pipeline
from app.core.events import event_bus


class GraphicAgent(BaseAgent):
    def __init__(self, pipeline: ContentPipeline | None = None) -> None:
        super().__init__(
            agent_id="graphic",
            name="Julian Reed",
            role="design_specialist",
            metadata={"tier": "epic", "legacy_name": "Graphic"},
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
        elif task == "create_graphic_prompt":
            request = GraphicRequest.model_validate(ctx.get("request", ctx))
            item = self.create_graphic_prompt(request)
            result = {"item": item.model_dump(mode="json")}
        elif task == "generate_graphic":
            request = GraphicRequest.model_validate(ctx.get("request", ctx))
            item = self.generate_graphic(request)
            result = {"item": item.model_dump(mode="json")}
        else:
            raise ValueError(f"Unsupported graphic task: {task}")
        return {"task": task, "ok": True, **result}

    def create_graphic_prompt(self, request: GraphicRequest):
        self._emit_received("create_graphic_prompt")
        self.status = "running"
        try:
            item = self.pipeline.graphic.create_graphic_prompt(request)
            self.status = "idle"
            self._emit_completed("create_graphic_prompt", {"content_id": item.id})
            return item
        except Exception as exc:
            self.status = "error"
            self._emit_failed("create_graphic_prompt", exc)
            raise

    def generate_graphic(self, request: GraphicRequest):
        self._emit_received("generate_graphic")
        self.status = "running"
        try:
            item = self.pipeline.graphic.generate_graphic(request)
            self.status = "idle"
            self._emit_completed("generate_graphic", {"content_id": item.id})
            return item
        except Exception as exc:
            self.status = "error"
            self._emit_failed("generate_graphic", exc)
            raise

    def health_check(self) -> dict[str, Any]:
        base = super().health_check()
        base["pipeline"] = self.pipeline.get_status()
        return base

    def _emit_received(
        self, command: str, payload: dict[str, Any] | None = None
    ) -> None:
        event_bus.emit(
            "graphic.command.received",
            self.id,
            "Graphic command received",
            {"command": command, **(payload or {})},
        )

    def _emit_completed(
        self, command: str, payload: dict[str, Any] | None = None
    ) -> None:
        event_bus.emit(
            "graphic.command.completed",
            self.id,
            "Graphic command completed",
            {"command": command, **(payload or {})},
        )

    def _emit_failed(self, command: str, exc: Exception) -> None:
        event_bus.emit(
            "graphic.command.failed",
            self.id,
            "Graphic command failed",
            {"command": command, "error": str(exc)},
        )
