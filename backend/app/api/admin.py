from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.audit_service import AuditService
from app.audit.models import AuditLogCreate
from app.auth.dependencies import get_current_user
from app.auth.models import AuthSession
from app.auth.password import hash_password
from app.core.config import get_settings
from app.core.responses import fail, ok
from app.db.models import User
from app.db.session import get_db_session

router = APIRouter(prefix="/api/admin", tags=["admin"])


class CreateUserRequest(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)
    role: str = "viewer"
    display_name: str = ""


class UpdateUserRequest(BaseModel):
    role: str | None = None
    display_name: str | None = None
    is_active: bool | None = None


def _require_admin(user: AuthSession) -> None:
    if user.role != "admin":
        raise PermissionError("Admin role required")


def _sanitize_user(row: User) -> dict[str, Any]:
    return {
        "id": row.id,
        "email": row.email,
        "display_name": row.display_name,
        "role": row.role,
        "is_active": row.is_active,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


def _safety_check_payload() -> dict[str, Any]:
    settings = get_settings()
    blockers: list[str] = []
    warnings: list[str] = []
    default_secret = "dev-only-change-before-production"

    if settings.is_production:
        if not settings.dry_run:
            if settings.production_safety_lock:
                blockers.append(
                    "DRY_RUN must remain true while PRODUCTION_SAFETY_LOCK is enabled."
                )
            elif not settings.production_allow_live_actions:
                blockers.append(
                    "Live mode requires PRODUCTION_ALLOW_LIVE_ACTIONS=true when DRY_RUN=false."
                )

        if settings.live_trading_ack and settings.jwt_secret_key.strip() == default_secret:
            blockers.append("LIVE_TRADING_ACK cannot be enabled with default JWT secret.")

        if not settings.social_dry_run and (
            not settings.social_approval_required
            or not settings.social_real_posting_approved
        ):
            blockers.append(
                "Real social posting requires approval-required mode and SOCIAL_REAL_POSTING_APPROVED=true."
            )

        if not settings.iot_dry_run and (
            not settings.iot_require_confirmation
            or not settings.iot_real_actions_approved
        ):
            blockers.append(
                "Real IoT actions require confirmation and IOT_REAL_ACTIONS_APPROVED=true."
            )

        if settings.jwt_secret_key.strip() in {"", default_secret}:
            blockers.append("JWT_SECRET_KEY must not be default in production.")

        if settings.default_admin_password.strip() in {"", default_secret}:
            blockers.append("DEFAULT_ADMIN_PASSWORD must not be default in production.")

        if "*" in settings.cors_origins_list and settings.cors_allow_credentials:
            blockers.append(
                "CORS wildcard cannot be used when credentials are allowed in production."
            )
    else:
        if not settings.auth_enabled:
            warnings.append("AUTH_ENABLED=false in non-production mode.")
        if not settings.metrics_auth_required:
            warnings.append("METRICS_AUTH_REQUIRED=false in non-production mode.")

    score = max(0, 100 - (len(blockers) * 20) - (len(warnings) * 5))
    return {
        "status": "safe" if not blockers else "blocked",
        "warnings": warnings,
        "blockers": blockers,
        "score": score,
    }


@router.get("/safety-check")
def safety_check(current_user: AuthSession = Depends(get_current_user)):
    try:
        _require_admin(current_user)
    except PermissionError as exc:
        return fail("AUTH_FORBIDDEN", str(exc))
    payload = _safety_check_payload()
    return ok(payload)


@router.get("/audit-logs")
def audit_logs(
    limit: int = 100,
    offset: int = 0,
    current_user: AuthSession = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    try:
        _require_admin(current_user)
    except PermissionError as exc:
        return fail("AUTH_FORBIDDEN", str(exc))

    items = AuditService(session).list(limit=limit, offset=offset)
    return ok({"items": [item.model_dump(mode="json") for item in items]})


@router.get("/users")
def users(
    current_user: AuthSession = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    try:
        _require_admin(current_user)
    except PermissionError as exc:
        return fail("AUTH_FORBIDDEN", str(exc))
    rows = session.execute(select(User).order_by(User.created_at.desc())).scalars().all()
    return ok({"users": [_sanitize_user(row) for row in rows]})


@router.post("/users")
def create_user(
    req: CreateUserRequest,
    current_user: AuthSession = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    try:
        _require_admin(current_user)
    except PermissionError as exc:
        return fail("AUTH_FORBIDDEN", str(exc))

    existing = session.execute(select(User).where(User.email == req.email)).scalar_one_or_none()
    if existing is not None:
        return fail("USER_EXISTS", "A user with that email already exists.")

    row = User(
        email=req.email,
        password_hash=hash_password(req.password),
        role=req.role,
        display_name=req.display_name,
        is_active=True,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    AuditService(session).log(
        AuditLogCreate(
            actor_user_id="",
            actor_email=current_user.username,
            action="admin.user.create",
            resource_type="user",
            resource_id=row.id,
            metadata={"email": row.email, "role": row.role},
        )
    )
    return ok({"user": _sanitize_user(row)})


@router.patch("/users/{user_id}")
def update_user(
    user_id: str,
    req: UpdateUserRequest,
    current_user: AuthSession = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    try:
        _require_admin(current_user)
    except PermissionError as exc:
        return fail("AUTH_FORBIDDEN", str(exc))

    row = session.get(User, user_id)
    if row is None:
        return fail("USER_NOT_FOUND", "User not found")
    if req.role is not None:
        row.role = req.role
    if req.display_name is not None:
        row.display_name = req.display_name
    if req.is_active is not None:
        row.is_active = req.is_active
    session.commit()
    session.refresh(row)
    AuditService(session).log(
        AuditLogCreate(
            actor_user_id="",
            actor_email=current_user.username,
            action="admin.user.update",
            resource_type="user",
            resource_id=row.id,
            metadata={
                "role": row.role,
                "display_name": row.display_name,
                "is_active": row.is_active,
            },
        )
    )
    return ok({"user": _sanitize_user(row)})


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    current_user: AuthSession = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    try:
        _require_admin(current_user)
    except PermissionError as exc:
        return fail("AUTH_FORBIDDEN", str(exc))

    row = session.get(User, user_id)
    if row is None:
        return fail("USER_NOT_FOUND", "User not found")
    if row.email == current_user.username and row.role == "admin":
        return fail(
            "ADMIN_SELF_DELETE_BLOCKED",
            "Current authenticated admin cannot be deactivated.",
        )
    row.is_active = False
    session.commit()
    session.refresh(row)
    AuditService(session).log(
        AuditLogCreate(
            actor_user_id="",
            actor_email=current_user.username,
            action="admin.user.deactivate",
            resource_type="user",
            resource_id=row.id,
            metadata={"email": row.email},
        )
    )
    return ok({"deactivated": True, "user_id": row.id})
