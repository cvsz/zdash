import pytest

from app.content.editor_service import EditorService
from app.content.graphic_service import GraphicService
from app.content.models import CreateContentRequest, GraphicRequest
from app.content.store import InMemoryContentStore


def _seed_content(store: InMemoryContentStore) -> str:
    editor = EditorService(store)
    item = editor.create_draft(CreateContentRequest(topic="zDash feature demo"))
    return item.id


def test_graphic_prompt_created() -> None:
    store = InMemoryContentStore()
    service = GraphicService(store)
    content_id = _seed_content(store)

    item = service.create_graphic_prompt(GraphicRequest(content_id=content_id))
    assert item.status.value == "graphic_requested"
    assert item.graphic_prompt


def test_mock_image_generated() -> None:
    store = InMemoryContentStore()
    service = GraphicService(store)
    content_id = _seed_content(store)

    item = service.generate_graphic(GraphicRequest(content_id=content_id))
    assert item.status.value == "graphic_ready"
    assert (item.graphic_asset_url or "").startswith("mock://image/")


def test_missing_content_handled_cleanly() -> None:
    store = InMemoryContentStore()
    service = GraphicService(store)
    with pytest.raises(ValueError):
        service.generate_graphic(GraphicRequest(content_id="missing"))


def test_dry_run_adapter_result_has_mock_provider() -> None:
    store = InMemoryContentStore()
    service = GraphicService(store)
    content_id = _seed_content(store)
    item = service.generate_graphic(GraphicRequest(content_id=content_id))
    metadata = item.metadata.get("image_generation", {})
    assert metadata.get("dry_run") is True
