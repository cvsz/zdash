from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.content.models import (
    ContentItem,
    ContentStatus,
    CreateContentRequest,
    PipelineRunResult,
)


class ContentNotFoundError(ValueError):
    pass


class InMemoryContentStore:
    def __init__(self) -> None:
        self._items: dict[str, ContentItem] = {}
        self._runs: dict[str, PipelineRunResult] = {}

    def create_item(self, request: CreateContentRequest) -> ContentItem:
        now = datetime.now(timezone.utc)
        item = ContentItem(
            id=str(uuid4()),
            title=request.topic[:100],
            content_type=request.content_type,
            status=ContentStatus.draft,
            brand=request.brand or "zDash",
            language=request.language or "en",
            tone=request.tone or "professional",
            topic=request.topic,
            platforms=request.platforms,
            metadata={"context": request.context},
            created_at=now,
            updated_at=now,
        )
        self._items[item.id] = item
        return item

    def get_item(self, content_id: str) -> ContentItem | None:
        return self._items.get(content_id)

    def list_items(self, status: ContentStatus | None = None) -> list[ContentItem]:
        items = list(self._items.values())
        return [i for i in items if i.status == status] if status else items

    def update_item(self, content_id: str, patch: dict) -> ContentItem:
        item = self.get_item(content_id)
        if item is None:
            raise ContentNotFoundError(content_id)
        data = item.model_dump()
        data.update(patch)
        data["updated_at"] = datetime.now(timezone.utc)
        updated = ContentItem(**data)
        self._items[content_id] = updated
        return updated

    def delete_item(self, content_id: str) -> bool:
        return self._items.pop(content_id, None) is not None

    def record_pipeline_run(self, result: PipelineRunResult) -> PipelineRunResult:
        self._runs[result.id] = result
        return result

    def list_pipeline_runs(
        self, content_id: str | None = None
    ) -> list[PipelineRunResult]:
        runs = list(self._runs.values())
        return [r for r in runs if r.content_id == content_id] if content_id else runs
