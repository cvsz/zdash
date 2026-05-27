from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.audit.audit_service import AuditService
from app.audit.models import AuditLogCreate
from app.db.base import Base


def _session_for_test(path: str) -> Session:
    engine = create_engine(
        f"sqlite:///{path}",
        future=True,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    return Session(engine)


def test_audit_service_logs_and_lists_entries(tmp_path):
    session = _session_for_test(str(tmp_path / "audit_service.db"))
    service = AuditService(session)

    created = service.log(
        AuditLogCreate(
            actor_user_id="user-1",
            actor_email="admin@example.com",
            action="scheduler.job.create",
            resource_type="scheduler_job",
            resource_id="job-1",
            result="success",
            ip_address="127.0.0.1",
            user_agent="pytest",
            metadata={"job_type": "backtest"},
        )
    )

    assert created.id
    assert created.actor_email == "admin@example.com"
    assert created.metadata["job_type"] == "backtest"

    rows = service.list(limit=10, offset=0)
    assert rows
    assert rows[0].action == "scheduler.job.create"
