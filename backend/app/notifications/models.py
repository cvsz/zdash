from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

AlertSeverity = Literal["info", "warning", "critical"]
AlertEventStatus = Literal["created", "sent", "suppressed", "failed"]
ChannelType = Literal["dry_run", "email", "webhook"]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


class AlertRule(BaseModel):
    id: str = Field(default_factory=lambda: f"rule_{uuid4().hex[:12]}")
    organization_id: str
    workspace_id: str
    name: str
    event_type: str
    severity: AlertSeverity = "warning"
    enabled: bool = True
    condition: str = "true"
    channels: list[str] = Field(default_factory=lambda: ["dry-run-default"])
    created_at: str = Field(default_factory=now_utc)
    updated_at: str = Field(default_factory=now_utc)


class AlertEvent(BaseModel):
    id: str = Field(default_factory=lambda: f"alert_{uuid4().hex[:12]}")
    organization_id: str
    workspace_id: str
    rule_id: str
    severity: AlertSeverity = "warning"
    title: str
    message: str
    payload: dict[str, Any] = Field(default_factory=dict)
    status: AlertEventStatus = "created"
    created_at: str = Field(default_factory=now_utc)


class NotificationChannel(BaseModel):
    id: str = Field(default_factory=lambda: f"chan_{uuid4().hex[:12]}")
    organization_id: str
    workspace_id: str
    name: str
    channel_type: ChannelType = "dry_run"
    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=now_utc)
    updated_at: str = Field(default_factory=now_utc)


class AlertRuleCreateRequest(BaseModel):
    name: str
    event_type: str
    severity: AlertSeverity = "warning"
    enabled: bool = True
    condition: str = "true"
    channels: list[str] = Field(default_factory=list)


class AlertRuleUpdateRequest(BaseModel):
    name: str | None = None
    severity: AlertSeverity | None = None
    enabled: bool | None = None
    condition: str | None = None
    channels: list[str] | None = None


class NotificationChannelCreateRequest(BaseModel):
    name: str
    channel_type: ChannelType = "dry_run"
    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)


class NotificationChannelUpdateRequest(BaseModel):
    name: str | None = None
    enabled: bool | None = None
    config: dict[str, Any] | None = None


class NotificationTestRequest(BaseModel):
    title: str = "Test notification"
    message: str = "Dry-run notification test"
    payload: dict[str, Any] = Field(default_factory=dict)
