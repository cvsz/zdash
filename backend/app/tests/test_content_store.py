from datetime import datetime, timezone

import pytest

from app.content.models import ContentStatus, CreateContentRequest, PipelineRunResult
from app.content.store import ContentNotFoundError, InMemoryContentStore


def test_store_create_get_list_update_delete_item() -> None:
    store = InMemoryContentStore()
    request = CreateContentRequest(topic="zDash release note")
    item = store.create_item(request)

    assert item.id
    assert store.get_item(item.id) is not None
    assert len(store.list_items()) == 1

    updated = store.update_item(item.id, {"status": ContentStatus.edited})
    assert updated.status == ContentStatus.edited

    assert store.delete_item(item.id) is True
    assert store.get_item(item.id) is None
    assert store.delete_item(item.id) is False


def test_store_update_missing_item_raises_domain_error() -> None:
    store = InMemoryContentStore()
    with pytest.raises(ContentNotFoundError):
        store.update_item("missing-id", {"status": ContentStatus.failed})


def test_store_records_pipeline_runs() -> None:
    store = InMemoryContentStore()
    run = PipelineRunResult(
        id="run-1",
        content_id="content-1",
        ok=True,
        status=ContentStatus.graphic_ready,
        steps=[{"step": "create_draft", "ok": True}],
        message="ok",
        started_at=datetime.now(timezone.utc),
        finished_at=datetime.now(timezone.utc),
        duration_ms=5,
    )
    store.record_pipeline_run(run)
    assert len(store.list_pipeline_runs()) == 1
    assert len(store.list_pipeline_runs(content_id="content-1")) == 1
    assert len(store.list_pipeline_runs(content_id="other")) == 0


def test_store_records_content_logs() -> None:
    store = InMemoryContentStore()
    entry = store.record_log(
        content_id="content-1",
        event_type="content.draft.created",
        source="EditorService",
        message="draft",
        payload={"content_id": "content-1"},
    )
    assert entry.id
    assert entry.content_id == "content-1"
    assert len(store.list_logs()) == 1
    assert len(store.list_logs(content_id="content-1")) == 1
