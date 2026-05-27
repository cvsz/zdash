from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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
        return fail("AUTH_FAILED", "Invalid username or password")

    if req.username in _login_attempts:
        _login_attempts[req.username].clear()
    auth_login_total.labels(status="success").inc()
    return ok(token_pair.model_dump())


@router.post("/refresh")
def refresh(req: RefreshRequest, session: Session = Depends(get_db_session)):
    token_pair = _auth_service(session).refresh(req.refresh_token)
    if token_pair is None:
        return fail("AUTH_REFRESH_FAILED", "Invalid refresh token")
    return ok(token_pair.model_dump())


@router.post("/logout")
def logout(req: LogoutRequest, session: Session = Depends(get_db_session)):
    revoked = _auth_service(session).logout(req.refresh_token)
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
