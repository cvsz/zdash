from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.content.models import (
    ContentItem,
    ContentPlatform,
    ContentStatus,
    ContentType,
    CreateContentRequest,
    PublishContentRequest,
)


def test_content_status_enum_contains_phase06_values() -> None:
    values = {status.value for status in ContentStatus}
    assert "draft" in values
    assert "graphic_ready" in values
    assert "approved" in values
    assert "rejected" in values


def test_content_platform_enum_contains_required_values() -> None:
    values = {platform.value for platform in ContentPlatform}
    assert values >= {"x", "tiktok", "facebook", "instagram", "linkedin", "blog", "generic"}


def test_content_item_defaults() -> None:
    item = ContentItem(
        id="item-1",
        title="zDash update",
        content_type=ContentType.announcement,
        brand="zDash",
        language="en",
        tone="professional",
        topic="weekly update",
    )
    assert item.status == ContentStatus.draft
    assert item.policy_passed is False
    assert item.policy_notes == []
    assert item.platforms == [ContentPlatform.generic]


def test_create_content_request_validation() -> None:
    with pytest.raises(ValidationError):
        CreateContentRequest(topic="", platforms=[ContentPlatform.x])
    with pytest.raises(ValidationError):
        CreateContentRequest(topic="ok", platforms=[])


def test_publish_request_confirmation_defaults_false() -> None:
    request = PublishContentRequest(content_id="abc123")
    assert request.confirmation is False


def test_datetime_fields_are_timezone_aware() -> None:
    item = ContentItem(
        id="item-2",
        title="tz",
        content_type=ContentType.text_post,
        brand="zDash",
        language="en",
        tone="professional",
        topic="timezone",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    assert item.created_at.tzinfo is not None
    assert item.updated_at.tzinfo is not None
