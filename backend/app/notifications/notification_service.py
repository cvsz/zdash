from __future__ import annotations

from app.core.config import get_settings
from app.notifications.alert_rules import DEFAULT_ALERT_RULE_DEFINITIONS
from app.notifications.channels import (
    dispatch_dry_run,
    dispatch_email,
    dispatch_webhook,
    sanitize_payload,
)
from app.notifications.models import (
    AlertEvent,
    AlertRule,
    AlertRuleCreateRequest,
    AlertRuleUpdateRequest,
    NotificationChannel,
    NotificationChannelCreateRequest,
    NotificationChannelUpdateRequest,
)


class NotificationService:
    def __init__(self) -> None:
        self.rules: dict[str, AlertRule] = {}
        self.channels: dict[str, NotificationChannel] = {}
        self.events: list[AlertEvent] = []

    def reset(self) -> None:
        self.rules.clear()
        self.channels.clear()
        self.events.clear()

    def ensure_defaults(self, organization_id: str, workspace_id: str) -> None:
        if not self.channels_for_tenant(organization_id, workspace_id):
            default_channel = NotificationChannel(
                organization_id=organization_id,
                workspace_id=workspace_id,
                name="dry-run-default",
                channel_type="dry_run",
                enabled=True,
                config={},
            )
            self.channels[default_channel.id] = default_channel
        existing_rule_names = {
            rule.name
            for rule in self.rules_for_tenant(organization_id, workspace_id)
        }
        if existing_rule_names:
            return
        default_channel_names = [
            channel.name
            for channel in self.channels_for_tenant(organization_id, workspace_id)
            if channel.enabled
        ]
        for definition in DEFAULT_ALERT_RULE_DEFINITIONS:
            rule = AlertRule(
                organization_id=organization_id,
                workspace_id=workspace_id,
                name=definition["name"],
                event_type=definition["event_type"],
                severity=definition["severity"],  # type: ignore[arg-type]
                enabled=True,
                condition="true",
                channels=default_channel_names,
            )
            self.rules[rule.id] = rule

    def rules_for_tenant(self, organization_id: str, workspace_id: str) -> list[AlertRule]:
        return [
            rule
            for rule in self.rules.values()
            if rule.organization_id == organization_id and rule.workspace_id == workspace_id
        ]

    def channels_for_tenant(
        self, organization_id: str, workspace_id: str
    ) -> list[NotificationChannel]:
        return [
            channel
            for channel in self.channels.values()
            if channel.organization_id == organization_id
            and channel.workspace_id == workspace_id
        ]

    def events_for_tenant(self, organization_id: str, workspace_id: str) -> list[AlertEvent]:
        return [
            event
            for event in self.events
            if event.organization_id == organization_id
            and event.workspace_id == workspace_id
        ]

    def create_rule(
        self,
        organization_id: str,
        workspace_id: str,
        payload: AlertRuleCreateRequest,
    ) -> AlertRule:
        self.ensure_defaults(organization_id, workspace_id)
        rule = AlertRule(
            organization_id=organization_id,
            workspace_id=workspace_id,
            name=payload.name.strip(),
            event_type=payload.event_type.strip(),
            severity=payload.severity,
            enabled=payload.enabled,
            condition=payload.condition,
            channels=payload.channels or ["dry-run-default"],
        )
        self.rules[rule.id] = rule
        return rule

    def update_rule(self, rule_id: str, payload: AlertRuleUpdateRequest) -> AlertRule | None:
        current = self.rules.get(rule_id)
        if current is None:
            return None
        data = current.model_dump()
        if payload.name is not None:
            data["name"] = payload.name.strip()
        if payload.severity is not None:
            data["severity"] = payload.severity
        if payload.enabled is not None:
            data["enabled"] = payload.enabled
        if payload.condition is not None:
            data["condition"] = payload.condition
        if payload.channels is not None:
            data["channels"] = payload.channels
        updated = AlertRule(**data)
        self.rules[rule_id] = updated
        return updated

    def delete_rule(self, rule_id: str) -> bool:
        return self.rules.pop(rule_id, None) is not None

    def create_channel(
        self,
        organization_id: str,
        workspace_id: str,
        payload: NotificationChannelCreateRequest,
    ) -> NotificationChannel:
        channel = NotificationChannel(
            organization_id=organization_id,
            workspace_id=workspace_id,
            name=payload.name.strip(),
            channel_type=payload.channel_type,
            enabled=payload.enabled,
            config=payload.config,
        )
        self.channels[channel.id] = channel
        return channel

    def update_channel(
        self,
        channel_id: str,
        payload: NotificationChannelUpdateRequest,
    ) -> NotificationChannel | None:
        current = self.channels.get(channel_id)
        if current is None:
            return None
        data = current.model_dump()
        if payload.name is not None:
            data["name"] = payload.name.strip()
        if payload.enabled is not None:
            data["enabled"] = payload.enabled
        if payload.config is not None:
            data["config"] = payload.config
        updated = NotificationChannel(**data)
        self.channels[channel_id] = updated
        return updated

    def delete_channel(self, channel_id: str) -> bool:
        return self.channels.pop(channel_id, None) is not None

    def emit_alert(
        self,
        *,
        organization_id: str,
        workspace_id: str,
        event_type: str,
        severity: str,
        title: str,
        message: str,
        payload: dict,
    ) -> dict:
        self.ensure_defaults(organization_id, workspace_id)
        matching_rules = [
            rule
            for rule in self.rules_for_tenant(organization_id, workspace_id)
            if rule.enabled and rule.event_type == event_type
        ]
        if not matching_rules:
            return {"matched_rules": 0, "dispatches": []}
        dispatches: list[dict] = []
        for rule in matching_rules:
            event = AlertEvent(
                organization_id=organization_id,
                workspace_id=workspace_id,
                rule_id=rule.id,
                severity=severity,  # type: ignore[arg-type]
                title=title,
                message=message,
                payload=sanitize_payload(payload),
                status="created",
            )
            self.events.insert(0, event)
            dispatches.extend(
                self._dispatch_channels(
                    organization_id=organization_id,
                    workspace_id=workspace_id,
                    channel_names=rule.channels,
                    title=title,
                    message=message,
                    payload=payload,
                )
            )
        return {"matched_rules": len(matching_rules), "dispatches": dispatches}

    def send_test_notification(
        self,
        *,
        organization_id: str,
        workspace_id: str,
        actor_user_id: str,
        title: str,
        message: str,
        payload: dict | None = None,
    ) -> dict:
        self.ensure_defaults(organization_id, workspace_id)
        dispatches = self._dispatch_channels(
            organization_id=organization_id,
            workspace_id=workspace_id,
            channel_names=[
                channel.name
                for channel in self.channels_for_tenant(organization_id, workspace_id)
                if channel.enabled
            ],
            title=title,
            message=message,
            payload=payload or {},
        )
        event = AlertEvent(
            organization_id=organization_id,
            workspace_id=workspace_id,
            rule_id="manual-test",
            severity="info",
            title=title,
            message=message,
            payload=sanitize_payload(payload or {}),
            status="created",
        )
        self.events.insert(0, event)
        return {
            "actor_user_id": actor_user_id,
            "event_id": event.id,
            "dispatches": dispatches,
        }

    def status(self) -> dict:
        settings = get_settings()
        return {
            "enabled": settings.notifications_enabled,
            "dry_run": settings.notification_dry_run,
            "rules_count": len(self.rules),
            "channels_count": len(self.channels),
            "events_count": len(self.events),
        }

    def _dispatch_channels(
        self,
        *,
        organization_id: str,
        workspace_id: str,
        channel_names: list[str],
        title: str,
        message: str,
        payload: dict,
    ) -> list[dict]:
        settings = get_settings()
        tenant_channels = {
            channel.name: channel
            for channel in self.channels_for_tenant(organization_id, workspace_id)
            if channel.enabled
        }
        dispatches: list[dict] = []
        for channel_name in channel_names:
            channel = tenant_channels.get(channel_name)
            if channel is None:
                continue
            if settings.notification_dry_run:
                dispatches.append(dispatch_dry_run(channel_name, title, message, payload))
                continue
            if channel.channel_type == "email":
                dispatches.append(dispatch_email(channel_name, title, message, payload))
            elif channel.channel_type == "webhook":
                dispatches.append(dispatch_webhook(channel_name, title, message, payload))
            else:
                dispatches.append(dispatch_dry_run(channel_name, title, message, payload))
        return dispatches


_notification_service: NotificationService | None = None


def get_notification_service() -> NotificationService:
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service


def reset_notification_service() -> None:
    global _notification_service
    _notification_service = None
