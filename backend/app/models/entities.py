from __future__ import annotations
 
# mypy: disable-error-code=call-arg

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, JSON, Text
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AgentRecord(SQLModel, table=True):
    __tablename__ = "agents"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str = Field(index=True, unique=True)
    role: str
    status: str = "idle"
    updated_at: datetime = Field(default_factory=utc_now)


class MessageRecord(SQLModel, table=True):
    __tablename__ = "messages"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    sender: str
    target: str
    message: str
    response: str
    created_at: datetime = Field(default_factory=utc_now, index=True)


class EventRecord(SQLModel, table=True):
    __tablename__ = "events"

    id: int | None = Field(default=None, primary_key=True)
    event_type: str = Field(index=True)
    source: str = Field(index=True)
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utc_now, index=True)


class TradingSignalRecord(SQLModel, table=True):
    __tablename__ = "trading_signals"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    symbol: str = Field(index=True)
    timeframe: str
    direction: str
    strategy: str
    confidence: float
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utc_now, index=True)


class ExecutionAttemptRecord(SQLModel, table=True):
    __tablename__ = "execution_attempts"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    mode: str
    executed: bool
    reason: str = ""
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utc_now, index=True)


class RiskDecisionRecord(SQLModel, table=True):
    __tablename__ = "risk_decisions"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    decision_type: str = Field(index=True)
    reason: str
    immutable: bool = False
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utc_now, index=True)


class HaltFlagRecord(SQLModel, table=True):
    __tablename__ = "halt_flags"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    halted: bool = False
    reason: str = ""
    locked: bool = False
    actor: str = "system"
    created_at: datetime = Field(default_factory=utc_now, index=True)


class SchedulerJobRecord(SQLModel, table=True):
    __tablename__ = "scheduler_jobs"

    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    interval_seconds: int
    status: str = "active"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class BacktestRunRecord(SQLModel, table=True):
    __tablename__ = "backtest_runs"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    strategy: str = Field(index=True)
    risk_per_trade: float
    primary_candidate: bool = False
    created_at: datetime = Field(default_factory=utc_now, index=True)


class BacktestResultRecord(SQLModel, table=True):
    __tablename__ = "backtest_results"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    run_id: str = Field(index=True)
    metrics: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utc_now, index=True)


class ContentItemRecord(SQLModel, table=True):
    __tablename__ = "content_items"

    id: str = Field(primary_key=True)
    topic: str
    body: str = Field(sa_column=Column(Text))
    state: str = Field(index=True)
    approved: bool = False
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utc_now, index=True)
    updated_at: datetime = Field(default_factory=utc_now)


class AuditLogRecord(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    action: str = Field(index=True)
    actor: str = Field(index=True)
    role: str = Field(index=True)
    target: str = ""
    detail: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utc_now, index=True)


class UserRecord(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    role: str = Field(index=True)
    is_active: bool = True
    created_at: datetime = Field(default_factory=utc_now, index=True)


class LiveModeApprovalRecord(SQLModel, table=True):
    __tablename__ = "live_mode_approvals"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    approved: bool = False
    actor: str = Field(index=True)
    reason: str
    created_at: datetime = Field(default_factory=utc_now, index=True)
