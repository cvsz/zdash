from __future__ import annotations

from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    AuditLog,
    BacktestResult,
    ContentItem,
    ContentPipelineRun,
    EventLog,
    HaltState,
    IoTActionLog,
    OptimizationResult,
    SchedulerJob,
    SchedulerRun,
    User,
)


class UserRepositoryProtocol(Protocol):
    def get_by_email(self, email: str) -> User | None: ...
    def create(
        self,
        email: str,
        password_hash: str,
        role: str = "viewer",
        display_name: str = "",
    ) -> User: ...
    def count(self) -> int: ...


class AuditRepositoryProtocol(Protocol):
    def create(self, **kwargs) -> AuditLog: ...


class EventLogRepositoryProtocol(Protocol):
    def create(self, event_type: str, source: str, message: str, payload: dict) -> EventLog: ...


class SchedulerRepositoryProtocol(Protocol):
    def upsert_job(self, job_id: str, **kwargs) -> SchedulerJob: ...
    def add_run(self, job_id: str, status: str, message: str = "", output: dict | None = None) -> SchedulerRun: ...


class BacktestRepositoryProtocol(Protocol):
    def create_backtest_result(
        self, strategy: str, symbol: str, timeframe: str, metrics: dict
    ) -> BacktestResult: ...
    def create_optimization_result(
        self, strategy: str, sort_metric: str, ranked_results: list, best_result: dict
    ) -> OptimizationResult: ...


class ContentRepositoryProtocol(Protocol):
    def create_content_item(self, **kwargs) -> ContentItem: ...
    def create_pipeline_run(
        self, content_item_id: str, stage: str, status: str, output: dict | None = None
    ) -> ContentPipelineRun: ...


class HaltStateRepositoryProtocol(Protocol):
    def set_state(self, halted: bool, reason: str, actor: str, locked: bool = False) -> HaltState: ...


class IoTActionLogRepositoryProtocol(Protocol):
    def create(self, **kwargs) -> IoTActionLog: ...


class UserRepository(UserRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

    def create(
        self,
        email: str,
        password_hash: str,
        role: str = "viewer",
        display_name: str = "",
    ) -> User:
        row = User(
            email=email,
            password_hash=password_hash,
            role=role,
            display_name=display_name,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def count(self) -> int:
        return len(self.db.execute(select(User.id)).scalars().all())


class AuditRepository(AuditRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> AuditLog:
        row = AuditLog(**kwargs)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row


class EventLogRepository(EventLogRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def create(self, event_type: str, source: str, message: str, payload: dict) -> EventLog:
        row = EventLog(
            event_type=event_type,
            source=source,
            message=message,
            payload_json=payload,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row


class SchedulerRepository(SchedulerRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def upsert_job(self, job_id: str, **kwargs) -> SchedulerJob:
        row = self.db.get(SchedulerJob, job_id)
        if row is None:
            row = SchedulerJob(id=job_id, **kwargs)
            self.db.add(row)
        else:
            for key, value in kwargs.items():
                setattr(row, key, value)
        self.db.commit()
        self.db.refresh(row)
        return row

    def add_run(
        self, job_id: str, status: str, message: str = "", output: dict | None = None
    ) -> SchedulerRun:
        row = SchedulerRun(
            job_id=job_id,
            status=status,
            message=message,
            output_json=output or {},
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row


class BacktestRepository(BacktestRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def create_backtest_result(
        self, strategy: str, symbol: str, timeframe: str, metrics: dict
    ) -> BacktestResult:
        row = BacktestResult(
            strategy=strategy,
            symbol=symbol,
            timeframe=timeframe,
            metrics_json=metrics,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def create_optimization_result(
        self, strategy: str, sort_metric: str, ranked_results: list, best_result: dict
    ) -> OptimizationResult:
        row = OptimizationResult(
            strategy=strategy,
            sort_metric=sort_metric,
            ranked_results_json=ranked_results,
            best_result_json=best_result,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row


class ContentRepository(ContentRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def create_content_item(self, **kwargs) -> ContentItem:
        row = ContentItem(**kwargs)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def create_pipeline_run(
        self, content_item_id: str, stage: str, status: str, output: dict | None = None
    ) -> ContentPipelineRun:
        row = ContentPipelineRun(
            content_item_id=content_item_id,
            stage=stage,
            status=status,
            output_json=output or {},
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row


class HaltStateRepository(HaltStateRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def set_state(
        self, halted: bool, reason: str, actor: str, locked: bool = False
    ) -> HaltState:
        row = HaltState(halted=halted, reason=reason, actor=actor, locked=locked)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row


class IoTActionLogRepository(IoTActionLogRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> IoTActionLog:
        row = IoTActionLog(**kwargs)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row
