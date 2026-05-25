from __future__ import annotations

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


class WaitlistStatus(str, Enum):
    pending = "pending"
    invited = "invited"
    activated = "activated"
    rejected = "rejected"


class InviteStatus(str, Enum):
    active = "active"
    used = "used"
    expired = "expired"
    revoked = "revoked"


class LaunchMode(str, Enum):
    private = "private"
    waitlist = "waitlist"
    invite_only = "invite_only"
    public = "public"


class PublicServiceStatus(str, Enum):
    operational = "operational"
    degraded = "degraded"
    partial_outage = "partial_outage"
    major_outage = "major_outage"
    maintenance = "maintenance"


class WaitlistEntry(BaseModel):
    id: str
    email: EmailStr
    name: str = ""
    organization_name: str = ""
    use_case: str = ""
    status: WaitlistStatus = WaitlistStatus.pending
    source: str = "public"
    invite_code_id: str | None = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class InviteCode(BaseModel):
    id: str
    code_hash: str
    label: str = ""
    status: InviteStatus = InviteStatus.active
    max_uses: int = 1
    used_count: int = 0
    expires_at: datetime | None = None
    created_by: str = "system"
    created_at: datetime
    updated_at: datetime


class PublicStatusComponent(BaseModel):
    id: str
    name: str
    status: PublicServiceStatus
    description: str = ""
    updated_at: datetime


class PublicStatusIncident(BaseModel):
    id: str
    title: str
    summary: str
    status: str
    severity: str
    public: bool = True
    started_at: datetime
    resolved_at: datetime | None = None
    updates: list[dict] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class LaunchReadinessCheck(BaseModel):
    id: str
    category: str
    name: str
    status: str
    severity: str
    message: str
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    checked_at: datetime


class TelemetryEvent(BaseModel):
    id: str
    organization_id: str | None = None
    workspace_id: str | None = None
    source: str
    event_name: str
    anonymous_id: str
    payload_summary: dict = Field(default_factory=dict)
    privacy_mode: str = "privacy_safe"
    created_at: datetime
