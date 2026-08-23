"""Tests for notification service and dispatch functionality."""

from unittest.mock import patch

import pytest

from app.notifications.models import (
    AlertRuleCreateRequest,
    NotificationChannelCreateRequest,
)
from app.notifications.notification_service import NotificationService


@pytest.fixture
def notification_service() -> NotificationService:
    """Create a fresh notification service instance."""
    return NotificationService()


@pytest.fixture
def tenant_data() -> dict:
    """Sample tenant data for tests."""
    return {
        "organization_id": "test_org",
        "workspace_id": "test_ws",
    }


def test_send_test_notification(
    notification_service: NotificationService, tenant_data: dict
) -> None:
    """Test sending a test notification."""
    with patch(
        "app.notifications.notification_service.dispatch_dry_run"
    ) as mock_dispatch:
        mock_dispatch.return_value = {"status": "dispatched", "channel": "dry-run"}

        result = notification_service.send_test_notification(
            organization_id=tenant_data["organization_id"],
            workspace_id=tenant_data["workspace_id"],
            actor_user_id="test_user",
            title="Test Title",
            message="Test Message",
        )

        assert "event_id" in result
        assert "dispatches" in result
        assert result["actor_user_id"] == "test_user"


def test_notification_ensures_defaults(
    notification_service: NotificationService, tenant_data: dict
) -> None:
    """Test that default channels and rules are created."""
    notification_service.ensure_defaults(
        tenant_data["organization_id"], tenant_data["workspace_id"]
    )

    channels = notification_service.channels_for_tenant(
        tenant_data["organization_id"], tenant_data["workspace_id"]
    )
    assert len(channels) > 0


def test_create_notification_channel(
    notification_service: NotificationService, tenant_data: dict
) -> None:
    """Test creating a notification channel."""
    payload = NotificationChannelCreateRequest(
        name="Test Channel",
        channel_type="dry_run",
        enabled=True,
    )

    channel = notification_service.create_channel(
        organization_id=tenant_data["organization_id"],
        workspace_id=tenant_data["workspace_id"],
        payload=payload,
    )

    assert channel.name == "Test Channel"
    assert channel.channel_type == "dry_run"
    assert channel.enabled is True


def test_update_notification_channel(
    notification_service: NotificationService, tenant_data: dict
) -> None:
    """Test updating a notification channel."""
    from app.notifications.models import NotificationChannelUpdateRequest

    payload = NotificationChannelCreateRequest(
        name="Original Channel",
        channel_type="dry_run",
    )

    channel = notification_service.create_channel(
        organization_id=tenant_data["organization_id"],
        workspace_id=tenant_data["workspace_id"],
        payload=payload,
    )

    update_payload = NotificationChannelUpdateRequest(
        name="Updated Channel",
        enabled=False,
    )

    updated = notification_service.update_channel(channel.id, update_payload)

    assert updated is not None
    assert updated.name == "Updated Channel"
    assert updated.enabled is False


def test_delete_notification_channel(
    notification_service: NotificationService, tenant_data: dict
) -> None:
    """Test deleting a notification channel."""
    payload = NotificationChannelCreateRequest(
        name="To Delete",
        channel_type="dry_run",
    )

    channel = notification_service.create_channel(
        organization_id=tenant_data["organization_id"],
        workspace_id=tenant_data["workspace_id"],
        payload=payload,
    )

    result = notification_service.delete_channel(channel.id)
    assert result is True

    channels = notification_service.channels_for_tenant(
        tenant_data["organization_id"], tenant_data["workspace_id"]
    )
    assert channel.id not in [c.id for c in channels]


def test_emit_alert_triggers_notifications(
    notification_service: NotificationService, tenant_data: dict
) -> None:
    """Test that emitting an alert triggers notifications."""
    rule_payload = AlertRuleCreateRequest(
        name="Test Rule",
        event_type="test_event",
        severity="warning",
    )

    notification_service.create_rule(
        organization_id=tenant_data["organization_id"],
        workspace_id=tenant_data["workspace_id"],
        payload=rule_payload,
    )

    with patch(
        "app.notifications.notification_service.dispatch_dry_run"
    ) as mock_dispatch:
        mock_dispatch.return_value = {"status": "sent"}

        result = notification_service.emit_alert(
            organization_id=tenant_data["organization_id"],
            workspace_id=tenant_data["workspace_id"],
            event_type="test_event",
            severity="warning",
            title="Alert Title",
            message="Alert Message",
            payload={"key": "value"},
        )

        assert result["matched_rules"] == 1
        assert len(result["dispatches"]) > 0


def test_notification_service_status(
    notification_service: NotificationService,
) -> None:
    """Test getting notification service status."""
    status = notification_service.status()

    assert "enabled" in status
    assert "dry_run" in status
    assert "rules_count" in status
    assert "channels_count" in status
    assert "events_count" in status
