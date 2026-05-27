from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth.auth_service import AuthService
from app.auth.password import hash_password
from app.db.base import Base
from app.db.repositories import RefreshTokenRepository, UserRepository


def _session_for_test(path: str) -> Session:
    engine = create_engine(
        f"sqlite:///{path}",
        future=True,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    return Session(engine)


def test_auth_service_login_refresh_and_logout(tmp_path):
    session = _session_for_test(str(tmp_path / "auth_service_login.db"))
    users = UserRepository(session)
    refresh_tokens = RefreshTokenRepository(session)
    auth_service = AuthService(users=users, refresh_tokens=refresh_tokens)

    users.create(
        email="operator@example.com",
        password_hash=hash_password("safe-password"),
        role="operator",
    )

    token_pair = auth_service.login("operator@example.com", "safe-password")
    assert token_pair is not None
    assert token_pair.access_token
    assert token_pair.refresh_token
    assert token_pair.role == "operator"

    refreshed = auth_service.refresh(token_pair.refresh_token)
    assert refreshed is not None
    assert refreshed.refresh_token != token_pair.refresh_token

    assert auth_service.logout(refreshed.refresh_token) is True
    assert auth_service.refresh(refreshed.refresh_token) is None


def test_auth_service_bootstrap_admin_only_when_empty(tmp_path):
    session = _session_for_test(str(tmp_path / "auth_service_bootstrap.db"))
    users = UserRepository(session)
    refresh_tokens = RefreshTokenRepository(session)
    auth_service = AuthService(users=users, refresh_tokens=refresh_tokens)

    created, detail = auth_service.bootstrap_admin("admin", "safe-password")
    assert created is True
    assert detail == "admin"

    created_again, detail_again = auth_service.bootstrap_admin("admin2", "safe-password")
    assert created_again is False
    assert "only allowed" in detail_again
