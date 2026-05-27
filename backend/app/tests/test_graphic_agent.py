from app.agents.editor import EditorAgent
from app.agents.graphic import GraphicAgent
from app.agents.registry import bootstrap_agents, registry
from app.content.models import CreateContentRequest, GraphicRequest
from app.core.events import event_bus


def test_graphic_agent_is_registered() -> None:
    bootstrap_agents()
    graphic = registry.get("graphic")
    assert graphic is not None
    assert graphic.id == "graphic"
    assert graphic.name == "Julian Reed"


def test_graphic_agent_can_generate_graphic_prompt() -> None:
    editor = EditorAgent()
    graphic = GraphicAgent()
    item = editor.create_draft(CreateContentRequest(topic="zDash dashboard visual"))
    generated = graphic.create_graphic_prompt(GraphicRequest(content_id=item.id))
    assert generated.graphic_prompt
    assert generated.status.value == "graphic_requested"


def test_graphic_agent_emits_events() -> None:
    editor = EditorAgent()
    graphic = GraphicAgent()
    item = editor.create_draft(CreateContentRequest(topic="zDash image content"))
    event_bus.clear()
    graphic.generate_graphic(GraphicRequest(content_id=item.id))
    event_types = {event.type for event in event_bus.list_events(limit=200)}
    assert "graphic.command.received" in event_types
    assert "graphic.command.completed" in event_types
