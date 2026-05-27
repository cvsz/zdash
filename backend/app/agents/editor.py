from __future__ import annotations

from typing import Any

from app.agents.base import AgentMessage, BaseAgent
from app.content.models import CreateContentRequest, EditContentRequest
from app.content.pipeline import ContentPipeline, get_content_pipeline
from app.core.events import event_bus


class EditorAgent(BaseAgent):
    def __init__(self, pipeline: ContentPipeline | None = None) -> None:
        super().__init__(
            agent_id="editor",
            name="Elena Voss",
            role="content_specialist",
            metadata={"tier": "epic", "legacy_name": "Editor"},
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
        elif task == "create_draft":
            create_request = CreateContentRequest.model_validate(
                ctx.get("request", ctx)
            )
            item = self.create_draft(create_request)
            result = {"item": item.model_dump(mode="json")}
        elif task == "edit_content":
            edit_request = EditContentRequest.model_validate(ctx.get("request", ctx))
            item = self.edit_content(edit_request)
            result = {"item": item.model_dump(mode="json")}
        elif task == "generate_variants":
            content_id = str(ctx.get("content_id", "")).strip()
            if not content_id:
                raise ValueError("content_id is required")
            count = int(ctx.get("count", 3))
            result = {"variants": self.generate_variants(content_id, count)}
        else:
            raise ValueError(f"Unsupported editor task: {task}")
        return {"task": task, "ok": True, **result}

    def create_draft(self, request: CreateContentRequest):
        self._emit_received("create_draft")
        self.status = "running"
        try:
            item = self.pipeline.editor.create_draft(request)
            self.status = "idle"
            self._emit_completed("create_draft", {"content_id": item.id})
            return item
        except Exception as exc:
            self.status = "error"
            self._emit_failed("create_draft", exc)
            raise

    def edit_content(self, request: EditContentRequest):
        self._emit_received("edit_content")
        self.status = "running"
        try:
            item = self.pipeline.editor.edit_content(request)
            self.status = "idle"
            self._emit_completed("edit_content", {"content_id": item.id})
            return item
        except Exception as exc:
            self.status = "error"
            self._emit_failed("edit_content", exc)
            raise

    def generate_variants(self, content_id: str, count: int = 3) -> list[str]:
        self._emit_received("generate_variants", {"content_id": content_id, "count": count})
        self.status = "running"
        try:
            variants = self.pipeline.editor.generate_variants(content_id, count)
            self.status = "idle"
            self._emit_completed(
                "generate_variants",
                {"content_id": content_id, "variant_count": len(variants)},
            )
            return variants
        except Exception as exc:
            self.status = "error"
            self._emit_failed("generate_variants", exc)
            raise

    def health_check(self) -> dict[str, Any]:
        base = super().health_check()
        base["pipeline"] = self.pipeline.get_status()
        return base

    def _emit_received(
        self, command: str, payload: dict[str, Any] | None = None
    ) -> None:
        event_bus.emit(
            "editor.command.received",
            self.id,
            "Editor command received",
            {"command": command, **(payload or {})},
        )

    def _emit_completed(
        self, command: str, payload: dict[str, Any] | None = None
    ) -> None:
        event_bus.emit(
            "editor.command.completed",
            self.id,
            "Editor command completed",
            {"command": command, **(payload or {})},
        )

    def _emit_failed(self, command: str, exc: Exception) -> None:
        event_bus.emit(
            "editor.command.failed",
            self.id,
            "Editor command failed",
            {"command": command, "error": str(exc)},
        )
