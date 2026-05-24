from fastapi import APIRouter, Depends

from app.core.auth import CurrentUser, require_roles
from app.core.database import session_scope
from app.core.responses import ok
from app.repositories import Repository

router = APIRouter(prefix='/api/audit', tags=['audit'])


@router.get('')
def list_audit(limit: int = 100, offset: int = 0, current_user: CurrentUser = Depends(require_roles('admin', 'operator'))):
    with session_scope() as session:
        rows = Repository(session).list_audit_logs(limit=limit, offset=offset)
    return ok(
        {
            'items': [
                {
                    'id': r.id,
                    'action': r.action,
                    'actor': r.actor,
                    'role': r.role,
                    'target': r.target,
                    'detail': r.detail,
                    'created_at': r.created_at.isoformat(),
                }
                for r in rows
            ]
        }
    )
