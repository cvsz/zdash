from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.content.editor_service import EditorService
from app.content.graphic_service import GraphicService
from app.content.models import (
    ApproveContentRequest,
    ContentPlatform,
    ContentStatus,
    CreateContentRequest,
    EditContentRequest,
    GraphicRequest,
    PipelineRunResult,
    PublishContentRequest,
    ScheduleContentRequest,
)
from app.content.social_service import SocialService
from app.content.store import InMemoryContentStore
from app.core.config import get_settings
from app.core.events import event_bus


class ContentPipeline:
    def __init__(self, store: InMemoryContentStore | None = None) -> None:
        self.settings = get_settings()
        self.store = store or InMemoryContentStore()
        self.editor = EditorService(self.store)
        self.graphic = GraphicService(self.store)
        self.social = SocialService(self.store)

    def run_full_pipeline(self, request: CreateContentRequest) -> PipelineRunResult:
        started = datetime.now(timezone.utc)
        run_id = str(uuid4())
        steps: list[dict] = []
        content_id = ""
        self._emit_pipeline_event(
            "content.pipeline.started",
            "ContentPipeline",
            "Pipeline started",
            {"run_id": run_id},
        )
        try:
            item = self.editor.create_draft(request)
            content_id = item.id
            self._record_step(
                steps, "create_draft", content_id=content_id, message="Draft created"
            )

            item = self.editor.edit_content(
                EditContentRequest(
                    content_id=item.id,
                    instructions=None,
                    tone=request.tone,
                    language=request.language,
                )
            )
            self._record_step(
                steps, "edit_content", content_id=content_id, message="Content edited"
            )

            if not item.policy_passed:
                self._record_step(
                    steps,
                    "policy_check",
                    ok=False,
                    content_id=content_id,
                    message="Policy failed",
                )
                self.store.update_item(item.id, {"status": ContentStatus.rejected})
                raise ValueError("policy failed")

            self._record_step(
                steps, "policy_check", content_id=content_id, message="Policy passed"
            )
            self.graphic.create_graphic_prompt(GraphicRequest(content_id=item.id))
            self._record_step(
                steps,
                "create_graphic_prompt",
                content_id=content_id,
                message="Graphic prompt created",
            )
            self.graphic.generate_graphic(GraphicRequest(content_id=item.id))
            self._record_step(
                steps,
                "generate_graphic",
                content_id=content_id,
                message="Graphic generated",
            )
            stored_item = self.store.get_item(item.id)
            status = stored_item.status if stored_item else ContentStatus.failed
            ok = True
            msg = "pipeline completed (approval and publish remain manual)"
            self._emit_pipeline_event(
                "content.pipeline.completed",
                "ContentPipeline",
                msg,
                {
                    "run_id": run_id,
                    "content_id": item.id,
                    "auto_approved": False,
                    "auto_published": False,
                },
            )
        except Exception as exc:
            ok = False
            if content_id:
                stored_item = self.store.get_item(content_id)
                status = stored_item.status if stored_item else ContentStatus.failed
            else:
                status = ContentStatus.failed
            msg = str(exc)
            steps.append({"step": "failed", "ok": False, "error": msg})
            self._emit_pipeline_event(
                "content.pipeline.failed",
                "ContentPipeline",
                msg,
                {"run_id": run_id, "content_id": content_id},
            )

        finished = datetime.now(timezone.utc)
        result = PipelineRunResult(
            id=run_id,
            content_id=content_id,
            ok=ok,
            status=status,
            steps=steps,
            message=msg,
            started_at=started,
            finished_at=finished,
            duration_ms=max(0, int((finished - started).total_seconds() * 1000)),
        )
        self.store.record_pipeline_run(result)
        return result

    def create_then_edit(self, request: CreateContentRequest) -> PipelineRunResult:
        started = datetime.now(timezone.utc)
        run_id = str(uuid4())
        steps: list[dict] = []
        content_id = ""
        try:
            item = self.editor.create_draft(request)
            content_id = item.id
            self._record_step(
                steps, "create_draft", content_id=content_id, message="Draft created"
            )
            item = self.editor.edit_content(
                EditContentRequest(
                    content_id=item.id,
                    tone=request.tone,
                    language=request.language,
                )
            )
            self._record_step(
                steps, "edit_content", content_id=content_id, message="Content edited"
            )
            ok = True
            status = item.status
            message = "draft and edit completed"
        except Exception as exc:
            ok = False
            status = ContentStatus.failed
            message = str(exc)
            steps.append({"step": "failed", "ok": False, "error": message})
        finished = datetime.now(timezone.utc)
        result = PipelineRunResult(
            id=run_id,
            content_id=content_id,
            ok=ok,
            status=status,
            steps=steps,
            message=message,
            started_at=started,
            finished_at=finished,
            duration_ms=max(0, int((finished - started).total_seconds() * 1000)),
        )
        self.store.record_pipeline_run(result)
        return result

    def generate_graphic(self, content_id: str) -> PipelineRunResult:
        started = datetime.now(timezone.utc)
        run_id = str(uuid4())
        steps: list[dict] = []
        try:
            self.graphic.create_graphic_prompt(GraphicRequest(content_id=content_id))
            self._record_step(
                steps,
                "create_graphic_prompt",
                content_id=content_id,
                message="Graphic prompt created",
            )
            item = self.graphic.generate_graphic(GraphicRequest(content_id=content_id))
            self._record_step(
                steps,
                "generate_graphic",
                content_id=content_id,
                message="Graphic generated",
            )
            ok = True
            status = item.status
            message = "graphic generation completed"
        except Exception as exc:
            ok = False
            status = ContentStatus.failed
            message = str(exc)
            steps.append({"step": "failed", "ok": False, "error": message})
        finished = datetime.now(timezone.utc)
        result = PipelineRunResult(
            id=run_id,
            content_id=content_id,
            ok=ok,
            status=status,
            steps=steps,
            message=message,
            started_at=started,
            finished_at=finished,
            duration_ms=max(0, int((finished - started).total_seconds() * 1000)),
        )
        self.store.record_pipeline_run(result)
        return result

    def schedule(
        self,
        content_id: str,
        scheduled_at: datetime,
        platforms: list[ContentPlatform] | None = None,
    ) -> PipelineRunResult:
        item = self.social.schedule_content(
            ScheduleContentRequest(
                content_id=content_id, scheduled_at=scheduled_at, platforms=platforms
            )
        )
        now = datetime.now(timezone.utc)
        result = PipelineRunResult(
            id=str(uuid4()),
            content_id=item.id,
            ok=True,
            status=item.status,
            steps=[{"step": "schedule", "ok": True}],
            message="scheduled",
            started_at=now,
            finished_at=now,
            duration_ms=0,
        )
        self.store.record_pipeline_run(result)
        return result

    def approve(
        self, content_id: str, approved_by: str = "operator"
    ) -> PipelineRunResult:
        item = self.social.approve_content(
            ApproveContentRequest(content_id=content_id, approved_by=approved_by)
        )
        now = datetime.now(timezone.utc)
        result = PipelineRunResult(
            id=str(uuid4()),
            content_id=item.id,
            ok=True,
            status=item.status,
            steps=[{"step": "approve", "ok": True}],
            message="approved",
            started_at=now,
            finished_at=now,
            duration_ms=0,
        )
        self.store.record_pipeline_run(result)
        return result

    def publish(
        self,
        content_id: str,
        platforms: list[ContentPlatform] | None = None,
        confirmation: bool = False,
    ) -> PipelineRunResult:
        self.social.publish_content(
            PublishContentRequest(
                content_id=content_id, platforms=platforms, confirmation=confirmation
            )
        )
        item = self.store.get_item(content_id)
        now = datetime.now(timezone.utc)
        result = PipelineRunResult(
            id=str(uuid4()),
            content_id=content_id,
            ok=True,
            status=item.status if item else ContentStatus.failed,
            steps=[{"step": "publish", "ok": True}],
            message="published",
            started_at=now,
            finished_at=now,
            duration_ms=0,
        )
        self.store.record_pipeline_run(result)
        return result

    def get_status(self) -> dict:
        return {
            "enabled": self.settings.content_pipeline_enabled,
            "store_type": self.settings.content_store,
            "social_dry_run": self.settings.social_dry_run,
            "approval_required": self.settings.social_approval_required,
            "auto_post_enabled": self.settings.social_auto_post_enabled,
            "item_count": len(self.store.list_items()),
            "pipeline_run_count": len(self.store.list_pipeline_runs()),
        }

    def _record_step(
        self,
        steps: list[dict],
        step_name: str,
        *,
        ok: bool = True,
        content_id: str,
        message: str,
    ) -> None:
        step = {
            "step": step_name,
            "ok": ok,
            "content_id": content_id,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        steps.append(step)
        self._emit_pipeline_event(
            "content.pipeline.step.completed",
            "ContentPipeline",
            f"{step_name} completed",
            step,
        )

    def _emit_pipeline_event(
        self, event_type: str, source: str, message: str, payload: dict
    ) -> None:
        event_bus.emit(event_type, source, message, payload)
        content_id = str(payload.get("content_id", "")).strip()
        if content_id:
            self.store.record_log(
                content_id=content_id,
                event_type=event_type,
                source=source,
                message=message,
                payload=payload,
            )


_content_pipeline: ContentPipeline | None = None


def get_content_pipeline() -> ContentPipeline:
    global _content_pipeline
    if _content_pipeline is None:
        _content_pipeline = ContentPipeline()
    return _content_pipeline


def reset_content_pipeline() -> None:
    global _content_pipeline
    _content_pipeline = None


content_pipeline = get_content_pipeline()
