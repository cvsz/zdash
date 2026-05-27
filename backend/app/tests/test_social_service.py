from datetime import datetime, timedelta, timezone

import pytest

from app.content.editor_service import EditorService
from app.content.models import (
    ApproveContentRequest,
    ContentStatus,
    CreateContentRequest,
    PublishContentRequest,
    ScheduleContentRequest,
)
from app.content.social_service import SocialService
from app.content.store import InMemoryContentStore
from app.core.config import get_settings


def _seed_content(service: SocialService, *, topic: str = "zDash update"):
    editor = EditorService(service.store)
    item = editor.create_draft(CreateContentRequest(topic=topic))
    return service.store.update_item(
        item.id, {"policy_passed": True, "status": ContentStatus.edited}
    )


def test_schedule_content() -> None:
    service = SocialService(InMemoryContentStore())
    item = _seed_content(service)
    scheduled_at = datetime.now(timezone.utc) + timedelta(hours=1)
    updated = service.schedule_content(
        ScheduleContentRequest(content_id=item.id, scheduled_at=scheduled_at)
    )
    assert updated.status == ContentStatus.scheduled
    assert updated.scheduled_at == scheduled_at


def test_approval_requires_policy_passed_true() -> None:
    service = SocialService(InMemoryContentStore())
    editor = EditorService(service.store)
    item = editor.create_draft(CreateContentRequest(topic="guaranteed profit strategy"))
    assert item.policy_passed is False
    with pytest.raises(ValueError):
        service.approve_content(ApproveContentRequest(content_id=item.id))


def test_publish_blocked_before_approval() -> None:
    service = SocialService(InMemoryContentStore())
    item = _seed_content(service)
    with pytest.raises(ValueError):
        service.publish_content(PublishContentRequest(content_id=item.id))


def test_dry_run_publish_simulated_after_approval() -> None:
    service = SocialService(InMemoryContentStore())
    item = _seed_content(service, topic="Backtesting educational simulation update")
    approved = service.approve_content(ApproveContentRequest(content_id=item.id))
    results = service.publish_content(PublishContentRequest(content_id=approved.id))
    assert results
    assert all(result.dry_run for result in results)
    stored = service.store.get_item(approved.id)
    assert stored is not None
    assert stored.status == ContentStatus.approved


def test_real_publish_blocked_without_confirmation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOCIAL_DRY_RUN", "false")
    monkeypatch.setenv("SOCIAL_AUTO_POST_ENABLED", "true")
    get_settings.cache_clear()
    service = SocialService(InMemoryContentStore())
    item = _seed_content(service, topic="educational simulation strategy update")
    approved = service.approve_content(ApproveContentRequest(content_id=item.id))
    with pytest.raises(ValueError):
        service.publish_content(
            PublishContentRequest(content_id=approved.id, confirmation=False)
        )


def test_rejected_content_cannot_be_posted() -> None:
    service = SocialService(InMemoryContentStore())
    item = _seed_content(service)
    service.store.update_item(item.id, {"status": ContentStatus.rejected})
    with pytest.raises(ValueError):
        service.publish_content(PublishContentRequest(content_id=item.id))
