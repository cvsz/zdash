from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    paused = "paused"
    completed = "completed"
    failed = "failed"
    disabled = "disabled"


class JobType(str, Enum):
    trading_scan = "trading_scan"
    risk_check = "risk_check"
    backtest = "backtest"
    content_pipeline = "content_pipeline"
    health_check = "health_check"
    iot_power_cycle = "iot_power_cycle"
    custom = "custom"


class ScheduleType(str, Enum):
    interval = "interval"
    cron = "cron"
    manual = "manual"


class ScheduledJob(BaseModel):
    id: str
    name: str
    job_type: JobType
    schedule_type: ScheduleType
    status: JobStatus = JobStatus.pending
    enabled: bool = True
    cron: str | None = None
    interval_seconds: int | None = Field(default=None, ge=1)
    payload: dict = Field(default_factory=dict)
    max_runtime_seconds: int = Field(default=300, ge=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None
    run_count: int = 0
    fail_count: int = 0


class JobRunResult(BaseModel):
    job_id: str
    job_type: JobType
    status: str
    ok: bool
    message: str
    output: dict = Field(default_factory=dict)
    started_at: datetime
    finished_at: datetime
    duration_ms: int = Field(default=0, ge=0)


class CreateJobRequest(BaseModel):
    name: str = Field(min_length=2)
    job_type: JobType
    schedule_type: ScheduleType
    cron: str | None = None
    interval_seconds: int | None = None
    payload: dict = Field(default_factory=dict)
    enabled: bool = True
    max_runtime_seconds: int = Field(default=300, ge=1)

    @model_validator(mode="after")
    def _validate_schedule_fields(self) -> "CreateJobRequest":
        if self.schedule_type == ScheduleType.interval:
            if self.interval_seconds is None or self.interval_seconds <= 0:
                raise ValueError("interval jobs require interval_seconds > 0")
        elif self.schedule_type == ScheduleType.cron:
            if not self.cron or not self.cron.strip():
                raise ValueError("cron jobs require cron string")
        return self
