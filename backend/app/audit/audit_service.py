from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.models import AuditLogCreate, AuditLogItem
from app.db.models import AuditLog
from app.db.repositories import AuditRepository


class AuditService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = AuditRepository(session)

    def log(self, entry: AuditLogCreate) -> AuditLogItem:
        row = self.repository.create(
            actor_user_id=entry.actor_user_id,
            actor_email=entry.actor_email,
            action=entry.action,
            resource_type=entry.resource_type,
            resource_id=entry.resource_id,
            result=entry.result,
            ip_address=entry.ip_address,
            user_agent=entry.user_agent,
            metadata_json=entry.metadata,
        )
        return self._to_item(row)

    def list(self, limit: int = 100, offset: int = 0) -> list[AuditLogItem]:
        stmt = (
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .offset(max(offset, 0))
            .limit(max(1, min(limit, 500)))
        )
        rows = self.session.execute(stmt).scalars().all()
        return [self._to_item(row) for row in rows]

    @staticmethod
    def _to_item(row: AuditLog) -> AuditLogItem:
        return AuditLogItem(
            id=row.id,
            actor_user_id=row.actor_user_id,
            actor_email=row.actor_email,
            action=row.action,
            resource_type=row.resource_type,
            resource_id=row.resource_id,
            result=row.result,
            ip_address=row.ip_address,
            user_agent=row.user_agent,
            metadata=row.metadata_json or {},
            created_at=row.created_at,
        )
