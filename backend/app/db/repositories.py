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
    RefreshToken,
    SchedulerJob,
    SchedulerRun,
    User,
)
from app.billing.models import (
    Subscription,
    UsageRecord,
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
    def get_by_id(self, user_id: str) -> User | None: ...


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


class RefreshTokenRepositoryProtocol(Protocol):
    def create(self, user_id: str, token_hash: str) -> RefreshToken: ...
    def get(self, token_hash: str) -> RefreshToken | None: ...
    def revoke(self, token_hash: str) -> bool: ...


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

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.get(User, user_id)


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


class RefreshTokenRepository(RefreshTokenRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: str, token_hash: str) -> RefreshToken:
        row = RefreshToken(user_id=user_id, token_hash=token_hash, is_revoked=False)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def get(self, token_hash: str) -> RefreshToken | None:
        return self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        ).scalar_one_or_none()

    def revoke(self, token_hash: str) -> bool:
        row = self.get(token_hash)
        if row is None:
            return False
        row.is_revoked = True
        self.db.commit()
        return True


class BillingRepositoryProtocol(Protocol):
    def get_subscription_by_org(self, organization_id: str) -> Subscription | None: ...
    def create_subscription(self, **kwargs) -> Subscription: ...
    def get_usage(self, organization_id: str, workspace_id: str, metric: str) -> UsageRecord | None: ...
    def record_usage(self, **kwargs) -> UsageRecord: ...


class BillingRepository(BillingRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def get_subscription_by_org(self, organization_id: str) -> Subscription | None:
        return self.db.execute(
            select(Subscription)
            .where(Subscription.organization_id == organization_id)
            .order_by(Subscription.created_at.desc())
        ).scalars().first()

    def create_subscription(self, **kwargs) -> Subscription:
        row = Subscription(**kwargs)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def get_usage(self, organization_id: str, workspace_id: str, metric: str) -> UsageRecord | None:
        return self.db.execute(
            select(UsageRecord)
            .where(UsageRecord.organization_id == organization_id)
            .where(UsageRecord.workspace_id == workspace_id)
            .where(UsageRecord.metric == metric)
            .order_by(UsageRecord.created_at.desc())
        ).scalars().first()

    def record_usage(self, **kwargs) -> UsageRecord:
        row = UsageRecord(**kwargs)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row
