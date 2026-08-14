"""Tests for alert rules functionality."""
from unittest.mock import patch

import pytest

from app.notifications.models import AlertRuleCreateRequest, AlertRuleUpdateRequest
from app.notifications.notification_service import NotificationService


@pytest.fixture
def notification_service() -> NotificationService:
    """Create a fresh notification service instance."""
    return NotificationService()


@pytest.fixture
def sample_rule_data() -> dict:
    """Sample rule creation data."""
    return {
        "organization_id": "test_org",
        "workspace_id": "test_ws",
        "name": "High Risk Alert",
        "event_type": "risk_threshold",
        "severity": "critical",
        "condition": "risk_score > 0.8",
    }


@pytest.fixture
def isolated_notification_service() -> NotificationService:
    """Create a fresh notification service with no pre-existing rules."""
    service = NotificationService()
    service.reset()
    return service


def test_create_alert_rule(
    notification_service: NotificationService, sample_rule_data: dict
) -> None:
    """Test creating an alert rule."""
    payload = AlertRuleCreateRequest(
        name=sample_rule_data["name"],
        event_type=sample_rule_data["event_type"],
        severity=sample_rule_data["severity"],
        condition=sample_rule_data["condition"],
    )

    rule = notification_service.create_rule(
        organization_id=sample_rule_data["organization_id"],
        workspace_id=sample_rule_data["workspace_id"],
        payload=payload,
    )

    assert rule.name == sample_rule_data["name"]
    assert rule.event_type == sample_rule_data["event_type"]
    assert rule.severity == sample_rule_data["severity"]
    assert rule.enabled is True
    assert rule.id.startswith("rule_")


def test_update_alert_rule(
    notification_service: NotificationService, sample_rule_data: dict
) -> None:
    """Test updating an alert rule."""
    payload = AlertRuleCreateRequest(
        name=sample_rule_data["name"],
        event_type=sample_rule_data["event_type"],
    )

    rule = notification_service.create_rule(
        organization_id=sample_rule_data["organization_id"],
        workspace_id=sample_rule_data["workspace_id"],
        payload=payload,
    )

    update_payload = AlertRuleUpdateRequest(
        name="Updated Alert Name",
        severity="warning",
        enabled=False,
    )

    updated_rule = notification_service.update_rule(rule.id, update_payload)

    assert updated_rule is not None
    assert updated_rule.name == "Updated Alert Name"
    assert updated_rule.severity == "warning"
    assert updated_rule.enabled is False


def test_delete_alert_rule(
    notification_service: NotificationService, sample_rule_data: dict
) -> None:
    """Test deleting an alert rule."""
    payload = AlertRuleCreateRequest(
        name=sample_rule_data["name"],
        event_type=sample_rule_data["event_type"],
    )

    rule = notification_service.create_rule(
        organization_id=sample_rule_data["organization_id"],
        workspace_id=sample_rule_data["workspace_id"],
        payload=payload,
    )

    result = notification_service.delete_rule(rule.id)
    assert result is True

    # Verify rule is deleted
    assert rule.id not in notification_service.rules


def test_rules_for_tenant(
    isolated_notification_service: NotificationService, sample_rule_data: dict
) -> None:
    """Test filtering rules by tenant."""
    payload = AlertRuleCreateRequest(
        name=sample_rule_data["name"],
        event_type=sample_rule_data["event_type"],
    )

    # Create rules for different tenants
    isolated_notification_service.create_rule(
        organization_id=sample_rule_data["organization_id"],
        workspace_id=sample_rule_data["workspace_id"],
        payload=payload,
    )

    other_payload = AlertRuleCreateRequest(
        name="Other Rule",
        event_type="other_event",
    )
    isolated_notification_service.create_rule(
        organization_id="other_org",
        workspace_id="other_ws",
        payload=other_payload,
    )

    rules = isolated_notification_service.rules_for_tenant(
        sample_rule_data["organization_id"], sample_rule_data["workspace_id"]
    )

    # ensure_defaults adds 8 default rules + 1 custom rule = 9 total
    assert len(rules) == 9
    # Verify our custom rule is in the list
    custom_rules = [r for r in rules if r.name == sample_rule_data["name"]]
    assert len(custom_rules) == 1


def test_emit_alert_with_matching_rule(
    notification_service: NotificationService, sample_rule_data: dict
) -> None:
    """Test emitting an alert that matches a rule."""
    payload = AlertRuleCreateRequest(
        name=sample_rule_data["name"],
        event_type=sample_rule_data["event_type"],
        severity="critical",
    )

    notification_service.create_rule(
        organization_id=sample_rule_data["organization_id"],
        workspace_id=sample_rule_data["workspace_id"],
        payload=payload,
    )

    with patch("app.notifications.notification_service.dispatch_dry_run") as mock_dispatch:
        mock_dispatch.return_value = {"status": "dispatched"}

        result = notification_service.emit_alert(
            organization_id=sample_rule_data["organization_id"],
            workspace_id=sample_rule_data["workspace_id"],
            event_type=sample_rule_data["event_type"],
            severity="critical",
            title="Test Alert",
            message="This is a test alert",
            payload={"test_key": "test_value"},
        )

        assert result["matched_rules"] == 1
        assert len(result["dispatches"]) > 0
