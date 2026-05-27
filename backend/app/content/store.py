from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from app.content.models import (
    ContentLogEntry,
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
        self._logs: dict[str, ContentLogEntry] = {}
        self._lock = Lock()

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
        with self._lock:
            self._items[item.id] = item
        return item

    def get_item(self, content_id: str) -> ContentItem | None:
        with self._lock:
            return self._items.get(content_id)

    def list_items(self, status: ContentStatus | None = None) -> list[ContentItem]:
        with self._lock:
            items = list(self._items.values())
        items.sort(key=lambda item: item.created_at)
        return [i for i in items if i.status == status] if status else items

    def update_item(self, content_id: str, patch: dict) -> ContentItem:
        with self._lock:
            item = self._items.get(content_id)
            if item is None:
                raise ContentNotFoundError(content_id)
            data = item.model_dump()
            data.update(patch)
            data["updated_at"] = datetime.now(timezone.utc)
            updated = ContentItem.model_validate(data)
            self._items[content_id] = updated
            return updated

    def delete_item(self, content_id: str) -> bool:
        with self._lock:
            deleted = self._items.pop(content_id, None) is not None
        return deleted

    def record_pipeline_run(self, result: PipelineRunResult) -> PipelineRunResult:
        with self._lock:
            self._runs[result.id] = result
        return result

    def list_pipeline_runs(
        self, content_id: str | None = None
    ) -> list[PipelineRunResult]:
        with self._lock:
            runs = list(self._runs.values())
        runs.sort(key=lambda run: run.started_at)
        return [r for r in runs if r.content_id == content_id] if content_id else runs

    def record_log(
        self,
        *,
        content_id: str,
        event_type: str,
        source: str,
        message: str,
        payload: dict | None = None,
    ) -> ContentLogEntry:
        entry = ContentLogEntry(
            id=str(uuid4()),
            content_id=content_id,
            event_type=event_type,
            source=source,
            message=message,
            payload=payload or {},
        )
        with self._lock:
            self._logs[entry.id] = entry
        return entry

    def list_logs(self, content_id: str | None = None) -> list[ContentLogEntry]:
        with self._lock:
            logs = list(self._logs.values())
        logs.sort(key=lambda log: log.created_at)
        if content_id is None:
            return logs
        return [entry for entry in logs if entry.content_id == content_id]
