from app.content.editor_service import EditorService
from app.content.models import CreateContentRequest, EditContentRequest
from app.content.store import InMemoryContentStore


def test_editor_create_draft_runs_policy_check() -> None:
    store = InMemoryContentStore()
    editor = EditorService(store)

    item = editor.create_draft(CreateContentRequest(topic="zDash release update"))
    assert item.draft_text
    assert item.policy_passed is True
    assert item.status.value == "draft"


def test_editor_edit_content_updates_text_and_status() -> None:
    store = InMemoryContentStore()
    editor = EditorService(store)
    created = editor.create_draft(CreateContentRequest(topic="zDash roadmap"))

    edited = editor.edit_content(
        EditContentRequest(
            content_id=created.id,
            instructions="Make it concise",
            tone="professional",
            language="en",
        )
    )
    assert edited.edited_text
    assert "Make it concise" in edited.edited_text
    assert edited.status.value == "edited"
    assert edited.policy_passed is True


def test_editor_adds_disclaimer_for_trading_content() -> None:
    store = InMemoryContentStore()
    editor = EditorService(store)
    item = editor.create_draft(CreateContentRequest(topic="backtest strategy update"))
    assert "Not financial advice" in (item.draft_text or "")
    edited = editor.edit_content(EditContentRequest(content_id=item.id))
    assert "Backtest results are not guaranteed future performance." in (
        edited.edited_text or ""
    )
    assert edited.policy_passed is True


def test_editor_generate_variants() -> None:
    store = InMemoryContentStore()
    editor = EditorService(store)
    item = editor.create_draft(CreateContentRequest(topic="weekly update"))

    variants = editor.generate_variants(item.id, count=3)
    assert len(variants) == 3
    assert "variant 1" in variants[0]


def test_editor_policy_failure_surfaces() -> None:
    store = InMemoryContentStore()
    editor = EditorService(store)
    item = editor.create_draft(CreateContentRequest(topic="guaranteed profit strategy"))
    assert item.policy_passed is False
    assert any("guaranteed-profit" in note.lower() for note in item.policy_notes)
