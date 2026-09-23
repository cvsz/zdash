"""Authenticated roles must match the current durable user record."""

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.audit import require_audit_reader
from app.auth.dependencies import get_current_user
from app.auth.jwt import create_access_token, create_refresh_token
from app.auth.models import AuthSession
from app.auth.rbac import Permission, has_permission
from app.core.config import get_settings
from app.db.base import Base
from app.db.repositories import UserRepository


@pytest.fixture
def db(tmp_path: Path) -> Generator[Session, None, None]:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'auth_dependency.db'}",
        future=True,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture
def enabled_auth(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    monkeypatch.setenv("AUTH_ENABLED", "true")
    monkeypatch.setenv("JWT_SECRET_KEY", "isolated-test-key-with-no-production-use")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def bearer(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def test_downgraded_user_cannot_reuse_old_admin_claim(
    enabled_auth: None, db: Session
) -> None:
    user = UserRepository(db).create(
        email="role-test@example.invalid",
        password_hash="synthetic-test-hash",
        role="admin",
    )
    old_admin_token = create_access_token(user.email, role="admin")
    assert get_current_user(bearer(old_admin_token), session=db).role == "admin"

    user.role = "viewer"
    db.commit()

    current = get_current_user(bearer(old_admin_token), session=db)
    assert current.role == "viewer"
    assert not has_permission(current.role, Permission.HALT_RESUME_RISK)


def test_deactivated_user_loses_access_immediately(
    enabled_auth: None, db: Session
) -> None:
    user = UserRepository(db).create(
        email="inactive-test@example.invalid",
        password_hash="synthetic-test-hash",
        role="operator",
    )
    token = create_access_token(user.email, role="operator")
    assert get_current_user(bearer(token), session=db).role == "operator"

    user.is_active = False
    db.commit()

    with pytest.raises(HTTPException) as exc:
        get_current_user(bearer(token), session=db)
    assert exc.value.status_code == 401


def test_deleted_and_unknown_users_are_denied(enabled_auth: None, db: Session) -> None:
    token = create_access_token("missing@example.invalid", role="admin")
    with pytest.raises(HTTPException) as exc:
        get_current_user(bearer(token), session=db)
    assert exc.value.status_code == 401


def test_refresh_token_is_never_accepted_as_access(
    enabled_auth: None, db: Session
) -> None:
    UserRepository(db).create(
        email="refresh-test@example.invalid",
        password_hash="synthetic-test-hash",
        role="viewer",
    )
    token = create_refresh_token("refresh-test@example.invalid", role="viewer")
    with pytest.raises(HTTPException) as exc:
        get_current_user(bearer(token), session=db)
    assert exc.value.status_code == 401


def test_missing_credentials_fail_when_auth_is_enabled(
    enabled_auth: None, db: Session
) -> None:
    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials=None, session=db)
    assert exc.value.status_code == 401


def test_explicit_development_bypass_remains_local_only(
    monkeypatch: pytest.MonkeyPatch, db: Session
) -> None:
    monkeypatch.setenv("AUTH_ENABLED", "false")
    get_settings.cache_clear()
    session = get_current_user(credentials=None, session=db)
    assert session.username == "dev-user"
    assert session.role == "admin"


@pytest.mark.parametrize("role", ["admin", "operator"])
def test_audit_keeps_existing_read_roles(role: str) -> None:
    user = AuthSession(username="reader@example.invalid", role=role)
    assert require_audit_reader(current_user=user).role == role


@pytest.mark.parametrize("role", ["analyst", "viewer"])
def test_audit_denies_unprivileged_roles(role: str) -> None:
    user = AuthSession(username="reader@example.invalid", role=role)
    with pytest.raises(HTTPException) as exc:
        require_audit_reader(current_user=user)
    assert exc.value.status_code == 403
