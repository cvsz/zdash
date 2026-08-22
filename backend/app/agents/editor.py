from __future__ import annotations

from app.agents.base import BaseAgent
from app.content.models import EditContentRequest
from app.content.pipeline import ContentPipeline
from app.events import event_bus


class EditorAgent(BaseAgent):
    def __init__(self, pipeline: ContentPipeline | None = None):
        super().__init__(agent_id="editor", name="Elena Voss")
        self.pipeline = pipeline or ContentPipeline()

    def health_check(self):
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
        }

    def run_task(self, task: str, context: dict | None = None):
        context = context or {}
        if task == "health":
            result = self.health_check()
        elif task == "edit_content":
            request = EditContentRequest.model_validate(context.get("request", context))
            result = {"item": self.edit_content(request).model_dump(mode="json")}
        elif task == "generate_variants":
            content_id = str(context.get("content_id", "")).strip()
            if not content_id:
                raise ValueError("content_id is required")
            count = int(context.get("count", 3))
            result = {"variants": self.generate_variants(content_id, count)}
        else:
            raise ValueError(f"Unsupported editor task: {task}")
        return {"task": task, "ok": True, **result}

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
        self._emit_received(
            "generate_variants", {"content_id": content_id, "count": count}
        )
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

    def _emit_received(self, command: str, payload: dict | None = None) -> None:
        event_bus.emit(
            "editor.command.received",
            source="editor",
            message=f"Editor received {command}",
            payload=payload or {},
        )

    def _emit_completed(self, command: str, payload: dict | None = None) -> None:
        event_bus.emit(
            "editor.command.completed",
            source="editor",
            message=f"Editor completed {command}",
            payload=payload or {},
        )

    def _emit_failed(self, command: str, exc: Exception) -> None:
        event_bus.emit(
            "editor.command.failed",
            source="editor",
            message=f"Editor failed {command}: {exc}",
            severity="error",
            payload={"error": str(exc)},
        )
