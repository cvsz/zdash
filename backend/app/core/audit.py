from typing import Any

from app.core.database import session_scope
from app.repositories import Repository


def audit(
    action: str,
    actor: str,
    role: str,
    target: str = "",
    detail: dict[str, Any] | None = None,
) -> None:
    with session_scope() as session:
        Repository(session).add_audit_log(
            action=action, actor=actor, role=role, target=target, detail=detail or {}
        )
