from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

TaskType = Literal[
    "trading_scan",
    "risk_check",
    "backtest_run",
    "optimization_run",
    "content_pipeline_run",
    "content_publish_dry_run",
    "iot_status_check",
    "notification_dispatch",
    "audit_compaction",
    "backup_run",
    "custom",
]
TaskStatus = Literal["queued", "running", "completed", "failed", "retrying", "cancelled"]
WorkerHealth = Literal["idle", "running", "degraded", "offline"]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


class WorkerTask(BaseModel):
    id: str = Field(default_factory=lambda: f"task_{uuid4().hex[:12]}")
    organization_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    task_type: TaskType = "custom"
    status: TaskStatus = "queued"
    payload: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] | None = None
    error: str | None = None
    priority: int = 5
    attempts: int = 0
    max_retries: int = 3
    scheduled_at: str = Field(default_factory=now_utc)
    started_at: str | None = None
    finished_at: str | None = None
    created_at: str = Field(default_factory=now_utc)
    updated_at: str = Field(default_factory=now_utc)

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: int) -> int:
        return max(1, min(10, value))

    @field_validator("max_retries")
    @classmethod
    def validate_retries(cls, value: int) -> int:
        return max(0, min(10, value))


class WorkerStatus(BaseModel):
    worker_id: str
    hostname: str
    status: WorkerHealth = "idle"
    current_task_id: str | None = None
    processed_count: int = 0
    failed_count: int = 0
    last_heartbeat_at: str = Field(default_factory=now_utc)


class WorkerTaskCreateRequest(BaseModel):
    task_type: TaskType = "custom"
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: int = 5
