from __future__ import annotations
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class OpsMode(str, Enum):
    advisory = "advisory"
    semi_auto = "semi_auto"
    manual = "manual"


class IncidentSeverity(str, Enum):
    info = "info"
    warning = "warning"
    critical = "critical"
    emergency = "emergency"


class IncidentStatus(str, Enum):
    open = "open"
    acknowledged = "acknowledged"
    investigating = "investigating"
    mitigated = "mitigated"
    resolved = "resolved"
    closed = "closed"
    canceled = "canceled"


class RemediationStatus(str, Enum):
    proposed = "proposed"
    approved = "approved"
    running = "running"
    completed = "completed"
    failed = "failed"
    blocked = "blocked"
    skipped = "skipped"


class ChangeStatus(str, Enum):
    draft = "draft"
    pending_approval = "pending_approval"
    approved = "approved"
    rejected = "rejected"
    scheduled = "scheduled"
    implemented = "implemented"
    rolled_back = "rolled_back"
    canceled = "canceled"


class EnvironmentStatus(str, Enum):
    healthy = "healthy"
    degraded = "degraded"
    down = "down"
    maintenance = "maintenance"
    unknown = "unknown"


class SystemHealthSnapshot(BaseModel):
    id: str
    organization_id: str
    workspace_id: str
    environment: str = "local"
    status: EnvironmentStatus = EnvironmentStatus.unknown
    health_score: float = 0
    backend_ok: bool = True
    frontend_ok: bool = True
    database_ok: bool = True
    redis_ok: bool = True
    worker_ok: bool = True
    scheduler_ok: bool = True
    risk_guardian_ok: bool = True
    event_stream_ok: bool = True
    alerts_ok: bool = True
    metrics: dict = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Incident(BaseModel):
    id: str
    organization_id: str
    workspace_id: str
    title: str
    description: str = ""
    severity: IncidentSeverity = IncidentSeverity.warning
    status: IncidentStatus = IncidentStatus.open
    source: str = "ops"
    affected_services: list[str] = Field(default_factory=list)
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    assigned_to: str | None = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RemediationAction(BaseModel):
    id: str
    organization_id: str
    workspace_id: str
    incident_id: str
    playbook_id: str
    title: str
    description: str = ""
    status: RemediationStatus = RemediationStatus.proposed
    dry_run: bool = True
    requires_approval: bool = True
    approved_by: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    result: dict = Field(default_factory=dict)
    error: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SLO(BaseModel):
    id: str
    organization_id: str
    workspace_id: str
    name: str
    target_percent: float
    measurement_window_days: int = 30
    query: str = ""
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SLAStatus(BaseModel):
    organization_id: str
    workspace_id: str
    uptime_percent: float
    response_time_minutes: float
    resolution_time_hours: float
    target_uptime_percent: float
    target_response_minutes: float
    target_resolution_hours: float
    breached: bool = False
    breach_reasons: list[str] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class MaintenanceWindow(BaseModel):
    id: str
    organization_id: str
    workspace_id: str
    title: str
    description: str = ""
    starts_at: datetime
    ends_at: datetime
    status: str = "draft"
    affected_services: list[str] = Field(default_factory=list)
    created_by: str
    approved_by: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChangeRequest(BaseModel):
    id: str
    organization_id: str
    workspace_id: str
    title: str
    description: str = ""
    change_type: str = "config"
    status: ChangeStatus = ChangeStatus.draft
    risk_level: str = "medium"
    rollback_plan: str | None = None
    scheduled_at: datetime | None = None
    implemented_at: datetime | None = None
    requested_by: str
    approved_by: str | None = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FleetEnvironment(BaseModel):
    id: str
    organization_id: str
    workspace_id: str
    name: str
    environment_type: str = "local"
    release_channel: str = "stable"
    version: str = "0.0.0"
    status: EnvironmentStatus = EnvironmentStatus.unknown
    base_url: str = ""
    region: str = "local"
    metadata: dict = Field(default_factory=dict)
    last_heartbeat_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
