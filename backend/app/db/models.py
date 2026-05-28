from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
import uuid


def _id() -> str:
    return str(uuid.uuid4())


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(Base, Timestamped):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String, default="")
    role: Mapped[str] = mapped_column(String, default="viewer")
    password_hash: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class RefreshToken(Base, Timestamped):
    __tablename__ = "refresh_tokens"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String, unique=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)


class AuditLog(Base, Timestamped):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    actor_user_id: Mapped[str] = mapped_column(String, default="")
    actor_email: Mapped[str] = mapped_column(String, index=True)
    action: Mapped[str] = mapped_column(String, index=True)
    resource_type: Mapped[str] = mapped_column(String, default="")
    resource_id: Mapped[str] = mapped_column(String, default="")
    result: Mapped[str] = mapped_column(String, default="success")
    ip_address: Mapped[str] = mapped_column(String, default="")
    user_agent: Mapped[str] = mapped_column(String, default="")
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)


class EventLog(Base, Timestamped):
    __tablename__ = "event_logs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    event_type: Mapped[str] = mapped_column(String, index=True)
    source: Mapped[str] = mapped_column(String, index=True)
    message: Mapped[str] = mapped_column(Text, default="")
    payload_json: Mapped[dict] = mapped_column("payload", JSON, default=dict)


class SchedulerJob(Base, Timestamped):
    __tablename__ = "scheduler_jobs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    name: Mapped[str] = mapped_column(String, index=True)
    job_type: Mapped[str] = mapped_column(String, default="custom")
    schedule_type: Mapped[str] = mapped_column(String, default="interval")
    status: Mapped[str] = mapped_column(String, default="active")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    cron: Mapped[str | None] = mapped_column(String, nullable=True)
    interval_seconds: Mapped[int | None] = mapped_column(nullable=True)
    payload_json: Mapped[dict] = mapped_column("payload", JSON, default=dict)


class SchedulerRun(Base, Timestamped):
    __tablename__ = "scheduler_runs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    job_id: Mapped[str] = mapped_column(String, ForeignKey("scheduler_jobs.id"), index=True)
    status: Mapped[str] = mapped_column(String, default="queued")
    message: Mapped[str] = mapped_column(Text, default="")
    output_json: Mapped[dict] = mapped_column("output", JSON, default=dict)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class HaltState(Base, Timestamped):
    __tablename__ = "halt_state"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    halted: Mapped[bool] = mapped_column(Boolean, default=False)
    reason: Mapped[str] = mapped_column(Text, default="")
    actor: Mapped[str] = mapped_column(String, default="system")
    locked: Mapped[bool] = mapped_column(Boolean, default=False)
    payload_json: Mapped[dict] = mapped_column("payload", JSON, default=dict)


class BacktestResult(Base, Timestamped):
    __tablename__ = "backtest_results"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    strategy: Mapped[str] = mapped_column(String, index=True)
    symbol: Mapped[str] = mapped_column(String, index=True)
    timeframe: Mapped[str] = mapped_column(String, index=True)
    metrics_json: Mapped[dict] = mapped_column("metrics", JSON, default=dict)
    trades_json: Mapped[list] = mapped_column("trades", JSON, default=list)
    summary_json: Mapped[dict] = mapped_column("summary", JSON, default=dict)


class OptimizationResult(Base, Timestamped):
    __tablename__ = "optimization_results"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    strategy: Mapped[str] = mapped_column(String, index=True)
    sort_metric: Mapped[str] = mapped_column(String, default="profit_factor")
    ranked_results_json: Mapped[list] = mapped_column("ranked_results", JSON, default=list)
    best_result_json: Mapped[dict] = mapped_column("best_result", JSON, default=dict)
    params_json: Mapped[dict] = mapped_column("params", JSON, default=dict)


class ContentItem(Base, Timestamped):
    __tablename__ = "content_items"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    title: Mapped[str] = mapped_column(String, default="")
    topic: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, index=True, default="draft")
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    draft_text: Mapped[str] = mapped_column(Text, default="")
    edited_text: Mapped[str] = mapped_column(Text, default="")
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)


class ContentPipelineRun(Base, Timestamped):
    __tablename__ = "content_pipeline_runs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    content_item_id: Mapped[str] = mapped_column(
        String, ForeignKey("content_items.id"), index=True
    )
    stage: Mapped[str] = mapped_column(String, default="draft")
    status: Mapped[str] = mapped_column(String, default="queued")
    output_json: Mapped[dict] = mapped_column("output", JSON, default=dict)
    errors_json: Mapped[list] = mapped_column("errors", JSON, default=list)


class IoTActionLog(Base, Timestamped):
    __tablename__ = "iot_action_logs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    action: Mapped[str] = mapped_column(String, index=True)
    device_alias: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="dry_run")
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True)
    confirmation_required: Mapped[bool] = mapped_column(Boolean, default=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    payload_json: Mapped[dict] = mapped_column("payload", JSON, default=dict)

# removed circular imports
