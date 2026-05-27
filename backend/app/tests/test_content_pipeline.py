from datetime import datetime, timedelta, timezone

from app.content.models import ContentStatus, CreateContentRequest
from app.content.pipeline import ContentPipeline
from app.content.store import InMemoryContentStore


def test_full_pipeline_runs_editor_and_graphic_without_auto_publish() -> None:
    pipeline = ContentPipeline(InMemoryContentStore())
    request = CreateContentRequest(
        topic="Backtesting educational simulation weekly report",
        content_type="educational",
        platforms=["x", "linkedin"],
    )
    result = pipeline.run_full_pipeline(request)
    assert result.ok is True
    assert result.content_id
    item = pipeline.store.get_item(result.content_id)
    assert item is not None
    assert item.draft_text
    assert item.edited_text
    assert item.graphic_asset_url
    assert item.status == ContentStatus.graphic_ready
    assert item.status != ContentStatus.approved
    assert item.status != ContentStatus.posted


def test_full_pipeline_records_steps() -> None:
    pipeline = ContentPipeline(InMemoryContentStore())
    result = pipeline.run_full_pipeline(CreateContentRequest(topic="zDash weekly update"))
    step_names = [step["step"] for step in result.steps]
    assert "create_draft" in step_names
    assert "edit_content" in step_names
    assert "create_graphic_prompt" in step_names
    assert "generate_graphic" in step_names


def test_pipeline_stops_on_policy_failure() -> None:
    pipeline = ContentPipeline(InMemoryContentStore())
    result = pipeline.run_full_pipeline(
        CreateContentRequest(topic="Guaranteed profit strategy for market wins")
    )
    assert result.ok is False
    assert result.message == "policy failed"
    item = pipeline.store.get_item(result.content_id)
    assert item is not None
    assert item.status == ContentStatus.rejected


def test_pipeline_schedule_approve_publish_wrappers() -> None:
    pipeline = ContentPipeline(InMemoryContentStore())
    result = pipeline.run_full_pipeline(
        CreateContentRequest(topic="Educational simulation strategy note")
    )
    content_id = result.content_id
    scheduled = pipeline.schedule(
        content_id, datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    assert scheduled.ok is True
    approved = pipeline.approve(content_id)
    assert approved.ok is True
    published = pipeline.publish(content_id, confirmation=False)
    assert published.ok is True
    item = pipeline.store.get_item(content_id)
    assert item is not None
    assert item.status == ContentStatus.approved
