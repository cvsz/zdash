from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api import auth as auth_api
from app.auth.models import (
    AuthSession,
    BootstrapAdminRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
)
from app.auth.password import hash_password
from app.db.base import Base
from app.db.repositories import UserRepository


def _session_for_test(path: str) -> Session:
    engine = create_engine(
        f"sqlite:///{path}",
        future=True,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    return Session(engine)


def _assert_envelope(payload: dict) -> None:
    assert set(payload.keys()) == {"ok", "data", "error", "timestamp"}


def test_auth_api_login_refresh_logout_and_me(tmp_path):
    auth_api._login_attempts.clear()
    session = _session_for_test(str(tmp_path / "auth_api_login.db"))
    test_password = "test-password-for-local-auth"

    UserRepository(session).create(
        email="analyst@example.com",
        password_hash=hash_password(test_password),
        role="analyst",
    )

    login_body = auth_api.login(
        LoginRequest(username="analyst@example.com", password=test_password),
        session=session,
    )
    _assert_envelope(login_body)
    assert login_body["ok"] is True
    refresh_token = login_body["data"]["refresh_token"]

    refresh_body = auth_api.refresh(
        RefreshRequest(refresh_token=refresh_token),
        session=session,
    )
    _assert_envelope(refresh_body)
    assert refresh_body["ok"] is True
    rotated_refresh_token = refresh_body["data"]["refresh_token"]

    logout_body = auth_api.logout(
        LogoutRequest(refresh_token=rotated_refresh_token),
        session=session,
    )
    _assert_envelope(logout_body)
    assert logout_body["ok"] is True
    assert logout_body["data"]["revoked"] is True

    me_body = auth_api.me(current_user=AuthSession(username="analyst@example.com", role="analyst"))
    _assert_envelope(me_body)
    assert me_body["ok"] is True
    assert me_body["data"]["role"] == "analyst"


def test_auth_api_bootstrap_admin(tmp_path):
    session = _session_for_test(str(tmp_path / "auth_api_bootstrap.db"))
    bootstrap_password = "bootstrap-local-test-password"
    body = auth_api.bootstrap_admin(
        BootstrapAdminRequest(username="admin-local", password=bootstrap_password),
        session=session,
    )
    _assert_envelope(body)
    assert body["ok"] is True
    assert body["data"]["created"] is True
