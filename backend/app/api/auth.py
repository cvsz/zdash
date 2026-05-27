from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.audit.audit_service import AuditService
from app.audit.models import AuditLogCreate
from app.auth.auth_service import AuthService
from app.auth.dependencies import get_current_user
from app.auth.models import (
    BootstrapAdminRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
)
from app.core.observability import auth_login_total
from app.core.responses import fail, ok
from app.db.repositories import RefreshTokenRepository, UserRepository
from app.db.session import get_db_session

router = APIRouter(prefix="/api/auth", tags=["auth"])
_login_attempts: dict[str, deque[float]] = defaultdict(deque)
MAX_LOGIN_ATTEMPTS = 8
WINDOW_SECONDS = 300


def _auth_service(session: Session) -> AuthService:
    return AuthService(
        users=UserRepository(session),
        refresh_tokens=RefreshTokenRepository(session),
    )


@router.post("/login")
def login(req: LoginRequest, session: Session = Depends(get_db_session)):
    now = time.time()
    bucket = _login_attempts[req.username]
    while bucket and now - bucket[0] > WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= MAX_LOGIN_ATTEMPTS:
        return fail("LOGIN_RATE_LIMITED", "Too many login attempts. Try again later.")

    token_pair = _auth_service(session).login(req.username, req.password)
    if token_pair is None:
        bucket.append(now)
        auth_login_total.labels(status="failure").inc()
        AuditService(session).log(
            AuditLogCreate(
                actor_user_id="",
                actor_email=req.username,
                action="auth.login.failure",
                resource_type="auth",
                resource_id=req.username,
                result="failure",
                metadata={"reason": "invalid_credentials"},
            )
        )
        return fail("AUTH_FAILED", "Invalid username or password")

    if req.username in _login_attempts:
        _login_attempts[req.username].clear()
    auth_login_total.labels(status="success").inc()
    AuditService(session).log(
        AuditLogCreate(
            actor_user_id="",
            actor_email=token_pair.username,
            action="auth.login.success",
            resource_type="auth",
            resource_id=token_pair.username,
            result="success",
            metadata={"role": token_pair.role},
        )
    )
    return ok(token_pair.model_dump())


@router.post("/refresh")
def refresh(req: RefreshRequest, session: Session = Depends(get_db_session)):
    token_pair = _auth_service(session).refresh(req.refresh_token)
    if token_pair is None:
        AuditService(session).log(
            AuditLogCreate(
                actor_user_id="",
                actor_email="",
                action="auth.token.refresh",
                resource_type="auth",
                resource_id="",
                result="failure",
                metadata={"reason": "invalid_refresh_token"},
            )
        )
        return fail("AUTH_REFRESH_FAILED", "Invalid refresh token")
    AuditService(session).log(
        AuditLogCreate(
            actor_user_id="",
            actor_email=token_pair.username,
            action="auth.token.refresh",
            resource_type="auth",
            resource_id=token_pair.username,
            result="success",
            metadata={"role": token_pair.role},
        )
    )
    return ok(token_pair.model_dump())


@router.post("/logout")
def logout(req: LogoutRequest, session: Session = Depends(get_db_session)):
    revoked = _auth_service(session).logout(req.refresh_token)
    AuditService(session).log(
        AuditLogCreate(
            actor_user_id="",
            actor_email="",
            action="auth.logout",
            resource_type="auth",
            resource_id="",
            result="success" if revoked else "failure",
            metadata={"revoked": revoked},
        )
    )
    return ok({"revoked": revoked})


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return ok({"username": current_user.username, "role": current_user.role})


@router.post("/bootstrap-admin")
def bootstrap_admin(
    req: BootstrapAdminRequest | None = None,
    session: Session = Depends(get_db_session),
):
    request = req or BootstrapAdminRequest()
    created, detail = _auth_service(session).bootstrap_admin(
        request.username,
        request.password,
    )
    if not created:
        return fail("AUTH_BOOTSTRAP_BLOCKED", detail)
    return ok({"created": True, "username": detail, "role": "admin"})
