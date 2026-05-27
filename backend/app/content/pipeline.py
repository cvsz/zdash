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
    GraphicRequest,
    PipelineRunResult,
    PublishContentRequest,
    ScheduleContentRequest,
)
from app.content.social_service import SocialService
from app.content.store import InMemoryContentStore
from app.core.events import event_bus


class ContentPipeline:
    def __init__(self, store: InMemoryContentStore | None = None) -> None:
        self.store = store or InMemoryContentStore()
        self.editor = EditorService(self.store)
        self.graphic = GraphicService(self.store)
        self.social = SocialService(self.store)

    def run_full_pipeline(self, request: CreateContentRequest) -> PipelineRunResult:
        started = datetime.now(timezone.utc)
        run_id = str(uuid4())
        steps = []
        content_id = ""
        event_bus.emit(
            "content.pipeline.started",
            "ContentPipeline",
            "Pipeline started",
            {"run_id": run_id},
        )
        try:
            item = self.editor.create_draft(request)
            content_id = item.id
            steps.append({"step": "create_draft", "ok": True})
            item = self.editor.edit_content(
                request=type(
                    "Req",
                    (),
                    {
                        "content_id": item.id,
                        "instructions": None,
                        "tone": request.tone,
                        "language": request.language,
                    },
                )()
            )
            steps.append({"step": "edit_content", "ok": True})
            if not item.policy_passed:
                steps.append({"step": "policy_check", "ok": False})
                raise ValueError("policy failed")
            steps.append({"step": "policy_check", "ok": True})
            self.graphic.generate_graphic(GraphicRequest(content_id=item.id))
            steps.append({"step": "generate_graphic", "ok": True})
            stored_item = self.store.get_item(item.id)
            status = stored_item.status if stored_item else ContentStatus.failed
            ok = True
            msg = "pipeline completed"
            event_bus.emit(
                "content.pipeline.completed",
                "ContentPipeline",
                msg,
                {"run_id": run_id, "content_id": item.id},
            )
        except Exception as exc:
            ok = False
            status = ContentStatus.failed
            msg = str(exc)
            steps.append({"step": "failed", "ok": False, "error": msg})
            event_bus.emit(
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
            duration_ms=int((finished - started).total_seconds() * 1000),
        )
        self.store.record_pipeline_run(result)
        return result

    def create_then_edit(self, request: CreateContentRequest) -> PipelineRunResult:
        return self.run_full_pipeline(request)

    def generate_graphic(self, content_id: str) -> PipelineRunResult:
        item = self.store.get_item(content_id)
        return self.run_full_pipeline(
            CreateContentRequest(topic=item.topic if item else "")
        )

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
        return PipelineRunResult(
            id=str(uuid4()),
            content_id=item.id,
            ok=True,
            status=item.status,
            steps=[{"step": "schedule", "ok": True}],
            message="scheduled",
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            duration_ms=0,
        )

    def approve(
        self, content_id: str, approved_by: str = "operator"
    ) -> PipelineRunResult:
        item = self.social.approve_content(
            ApproveContentRequest(content_id=content_id, approved_by=approved_by)
        )
        return PipelineRunResult(
            id=str(uuid4()),
            content_id=item.id,
            ok=True,
            status=item.status,
            steps=[{"step": "approve", "ok": True}],
            message="approved",
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            duration_ms=0,
        )

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
        return PipelineRunResult(
            id=str(uuid4()),
            content_id=content_id,
            ok=True,
            status=item.status if item else ContentStatus.failed,
            steps=[{"step": "publish", "ok": True}],
            message="published",
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            duration_ms=0,
        )


content_pipeline = ContentPipeline()
