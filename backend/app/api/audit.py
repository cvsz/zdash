from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.auth.models import AuthSession
from app.core.database import session_scope
from app.core.responses import ok
from app.repositories import Repository

router = APIRouter(prefix="/api/audit", tags=["audit"])


def require_audit_reader(
    current_user: AuthSession = Depends(get_current_user),
) -> AuthSession:
    # Reuse the canonical auth dependency so a legacy audit endpoint cannot
    # accept a refresh JWT or outdated role claims from the legacy auth path.
    if current_user.role not in {"admin", "operator"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient role",
        )
    return current_user


@router.get("")
def list_audit(
    limit: int = 100,
    offset: int = 0,
    current_user: AuthSession = Depends(require_audit_reader),
):
    with session_scope() as session:
        rows = Repository(session).list_audit_logs(limit=limit, offset=offset)
    return ok(
        {
            "items": [
                {
                    "id": r.id,
                    "action": r.action,
                    "actor": r.actor,
                    "role": r.role,
                    "target": r.target,
                    "detail": r.detail,
                    "created_at": r.created_at.isoformat(),
                }
                for r in rows
            ]
        }
    )
