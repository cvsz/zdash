from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, col, select

from app.models.entities import (
    AgentRecord,
    AuditLogRecord,
    BacktestResultRecord,
    BacktestRunRecord,
    ContentItemRecord,
    EventRecord,
    ExecutionAttemptRecord,
    HaltFlagRecord,
    LiveModeApprovalRecord,
    MessageRecord,
    RiskDecisionRecord,
    SchedulerJobRecord,
    TradingSignalRecord,
    UserRecord,
)


class Repository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert_agent(self, name: str, role: str, status: str) -> AgentRecord:
        agent = self.session.exec(
            select(AgentRecord).where(AgentRecord.name == name)
        ).first()
        if agent is None:
            agent = AgentRecord(name=name, role=role, status=status)
            self.session.add(agent)
        else:
            agent.role = role
            agent.status = status
            agent.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return agent

    def list_agents(self) -> list[AgentRecord]:
        return list(self.session.exec(select(AgentRecord).order_by(AgentRecord.name)))

    def add_message(
        self, sender: str, target: str, message: str, response: str
    ) -> MessageRecord:
        row = MessageRecord(
            sender=sender, target=target, message=message, response=response
        )
        self.session.add(row)
        self.session.flush()
        return row

    def add_event(
        self, event_type: str, source: str, payload: dict[str, Any]
    ) -> EventRecord:
        row = EventRecord(event_type=event_type, source=source, payload=payload)
        self.session.add(row)
        self.session.flush()
        return row

    def list_events(self, limit: int = 100, offset: int = 0) -> list[EventRecord]:
        stmt = (
            select(EventRecord)
            .order_by(col(EventRecord.id).desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.exec(stmt))

    def add_trading_signal(self, signal: dict[str, Any]) -> TradingSignalRecord:
        row = TradingSignalRecord(
            symbol=signal.get("symbol", ""),
            timeframe=signal.get("timeframe", ""),
            direction=signal.get("direction", ""),
            strategy=signal.get("strategy", ""),
            confidence=float(signal.get("confidence", 0.0)),
            payload=signal,
        )
        self.session.add(row)
        self.session.flush()
        return row

    def add_execution_attempt(self, result: dict[str, Any]) -> ExecutionAttemptRecord:
        row = ExecutionAttemptRecord(
            mode=result.get("mode", "unknown"),
            executed=bool(result.get("executed", False)),
            reason=result.get("reason", ""),
            payload=result,
        )
        self.session.add(row)
        self.session.flush()
        return row

    def add_risk_decision(
        self,
        decision_type: str,
        reason: str,
        payload: dict[str, Any],
        immutable: bool = False,
    ) -> RiskDecisionRecord:
        row = RiskDecisionRecord(
            decision_type=decision_type,
            reason=reason,
            payload=payload,
            immutable=immutable,
        )
        self.session.add(row)
        self.session.flush()
        return row

    def latest_risk_decision(
        self, decision_type: str | None = None
    ) -> RiskDecisionRecord | None:
        stmt = select(RiskDecisionRecord)
        if decision_type is not None:
            stmt = stmt.where(RiskDecisionRecord.decision_type == decision_type)
        stmt = stmt.order_by(col(RiskDecisionRecord.created_at).desc())
        return self.session.exec(stmt).first()

    def set_halt_flag(
        self, halted: bool, reason: str, actor: str, locked: bool = False
    ) -> HaltFlagRecord:
        row = HaltFlagRecord(halted=halted, reason=reason, actor=actor, locked=locked)
        self.session.add(row)
        self.session.flush()
        return row

    def latest_halt_flag(self) -> HaltFlagRecord | None:
        stmt = select(HaltFlagRecord).order_by(col(HaltFlagRecord.created_at).desc())
        return self.session.exec(stmt).first()

    def upsert_scheduler_job(
        self, job_id: str, name: str, interval_seconds: int, status: str
    ) -> SchedulerJobRecord:
        row = self.session.get(SchedulerJobRecord, job_id)
        now = datetime.now(timezone.utc)
        if row is None:
            row = SchedulerJobRecord(
                id=job_id,
                name=name,
                interval_seconds=interval_seconds,
                status=status,
                created_at=now,
                updated_at=now,
            )
            self.session.add(row)
        else:
            row.name = name
            row.interval_seconds = interval_seconds
            row.status = status
            row.updated_at = now
        self.session.flush()
        return row

    def list_scheduler_jobs(self) -> list[SchedulerJobRecord]:
        return list(
            self.session.exec(
                select(SchedulerJobRecord).order_by(
                    col(SchedulerJobRecord.created_at).desc()
                )
            )
        )

    def add_backtest_run(
        self, strategy: str, risk_per_trade: float, primary_candidate: bool
    ) -> BacktestRunRecord:
        row = BacktestRunRecord(
            strategy=strategy,
            risk_per_trade=risk_per_trade,
            primary_candidate=primary_candidate,
        )
        self.session.add(row)
        self.session.flush()
        return row

    def add_backtest_result(
        self, run_id: str, metrics: dict[str, Any]
    ) -> BacktestResultRecord:
        row = BacktestResultRecord(run_id=run_id, metrics=metrics)
        self.session.add(row)
        self.session.flush()
        return row

    def list_backtest_results(self) -> list[BacktestResultRecord]:
        return list(
            self.session.exec(
                select(BacktestResultRecord).order_by(
                    col(BacktestResultRecord.created_at).desc()
                )
            )
        )

    def add_content_item(
        self,
        item_id: str,
        topic: str,
        body: str,
        state: str,
        approved: bool,
        payload: dict[str, Any],
    ) -> ContentItemRecord:
        row = ContentItemRecord(
            id=item_id,
            topic=topic,
            body=body,
            state=state,
            approved=approved,
            payload=payload,
        )
        self.session.add(row)
        self.session.flush()
        return row

    def update_content_item(
        self, item_id: str, **updates: Any
    ) -> ContentItemRecord | None:
        row = self.session.get(ContentItemRecord, item_id)
        if row is None:
            return None
        for key, value in updates.items():
            setattr(row, key, value)
        row.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return row

    def get_content_item(self, item_id: str) -> ContentItemRecord | None:
        return self.session.get(ContentItemRecord, item_id)

    def list_content_items(self) -> list[ContentItemRecord]:
        return list(
            self.session.exec(
                select(ContentItemRecord).order_by(col(ContentItemRecord.created_at).desc())
            )
        )

    def add_audit_log(
        self,
        action: str,
        actor: str,
        role: str,
        target: str = "",
        detail: dict[str, Any] | None = None,
    ) -> AuditLogRecord:
        row = AuditLogRecord(
            action=action, actor=actor, role=role, target=target, detail=detail or {}
        )
        self.session.add(row)
        self.session.flush()
        return row

    def list_audit_logs(
        self, limit: int = 100, offset: int = 0
    ) -> list[AuditLogRecord]:
        stmt = (
            select(AuditLogRecord)
            .order_by(col(AuditLogRecord.created_at).desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.exec(stmt))

    def get_user_by_username(self, username: str) -> UserRecord | None:
        return self.session.exec(
            select(UserRecord).where(UserRecord.username == username)
        ).first()

    def add_user(self, username: str, password_hash: str, role: str) -> UserRecord:
        row = UserRecord(username=username, password_hash=password_hash, role=role)
        self.session.add(row)
        self.session.flush()
        return row

    def add_live_mode_approval(
        self, actor: str, approved: bool, reason: str
    ) -> LiveModeApprovalRecord:
        row = LiveModeApprovalRecord(actor=actor, approved=approved, reason=reason)
        self.session.add(row)
        self.session.flush()
        return row

    def latest_live_mode_approval(self) -> LiveModeApprovalRecord | None:
        stmt = select(LiveModeApprovalRecord).order_by(
            col(LiveModeApprovalRecord.created_at).desc()
        )
        return self.session.exec(stmt).first()
