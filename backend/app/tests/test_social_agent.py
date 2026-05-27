from datetime import datetime, timedelta, timezone

import pytest

from app.agents.editor import EditorAgent
from app.agents.registry import bootstrap_agents, registry
from app.agents.social import SocialAgent
from app.content.models import (
    ApproveContentRequest,
    ContentStatus,
    CreateContentRequest,
    PublishContentRequest,
    ScheduleContentRequest,
)
from app.core.events import event_bus


def test_social_agent_is_registered() -> None:
    bootstrap_agents()
    social = registry.get("social")
    assert social is not None
    assert social.id == "social"
    assert social.name == "Maya Quinn"


def test_social_agent_can_schedule_content() -> None:
    editor = EditorAgent()
    social = SocialAgent()
    item = editor.create_draft(CreateContentRequest(topic="zDash schedule note"))
    approved_input = social.pipeline.store.update_item(
        item.id, {"policy_passed": True, "status": ContentStatus.edited}
    )
    scheduled = social.schedule_content(
        ScheduleContentRequest(
            content_id=approved_input.id,
            scheduled_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        )
    )
    assert scheduled.status == ContentStatus.scheduled


def test_social_agent_blocks_publish_without_approval() -> None:
    editor = EditorAgent()
    social = SocialAgent()
    item = editor.create_draft(CreateContentRequest(topic="zDash publish note"))
    social.pipeline.store.update_item(item.id, {"policy_passed": True, "status": ContentStatus.edited})
    with pytest.raises(ValueError):
        social.publish_content(PublishContentRequest(content_id=item.id))


def test_social_agent_emits_events() -> None:
    editor = EditorAgent()
    social = SocialAgent()
    item = editor.create_draft(CreateContentRequest(topic="educational simulation strategy post"))
    social.pipeline.store.update_item(item.id, {"policy_passed": True, "status": ContentStatus.edited})
    social.approve_content(ApproveContentRequest(content_id=item.id))
    event_bus.clear()
    social.publish_content(PublishContentRequest(content_id=item.id))
    event_types = {event.type for event in event_bus.list_events(limit=300)}
    assert "social.command.received" in event_types
    assert "social.command.completed" in event_types
