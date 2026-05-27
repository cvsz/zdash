from app.agents.editor import EditorAgent
from app.agents.registry import bootstrap_agents, registry
from app.content.models import CreateContentRequest
from app.core.events import event_bus


def test_editor_agent_is_registered() -> None:
    bootstrap_agents()
    editor = registry.get("editor")
    assert editor is not None
    assert editor.id == "editor"
    assert editor.name == "Elena Voss"


def test_editor_agent_can_create_draft() -> None:
    editor = EditorAgent()
    item = editor.create_draft(CreateContentRequest(topic="Educational simulation note"))
    assert item.id
    assert item.draft_text
    assert item.policy_passed is True


def test_editor_agent_emits_events() -> None:
    editor = EditorAgent()
    event_bus.clear()
    editor.create_draft(CreateContentRequest(topic="zDash update"))
    event_types = {event.type for event in event_bus.list_events(limit=200)}
    assert "editor.command.received" in event_types
    assert "editor.command.completed" in event_types
