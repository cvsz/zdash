from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api import admin as admin_api
from app.auth.models import AuthSession
from app.auth.password import hash_password
from app.db.base import Base
from app.db.models import User


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


def test_admin_users_crud_does_not_expose_password_hash(tmp_path):
    session = _session_for_test(str(tmp_path / "admin_users.db"))
    admin_password = "admin-local-password"
    admin = User(
        email="admin@example.com",
        password_hash=hash_password(admin_password),
        role="admin",
        display_name="Admin",
        is_active=True,
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)

    current_user = AuthSession(username="admin@example.com", role="admin")
    new_user_password = "viewer-local-password"

    create_body = admin_api.create_user(
        admin_api.CreateUserRequest(
            email="viewer@example.com",
            password=new_user_password,
            role="viewer",
            display_name="Viewer",
        ),
        current_user=current_user,
        session=session,
    )
    _assert_envelope(create_body)
    assert create_body["ok"] is True
    created_user_id = create_body["data"]["user"]["id"]
    assert "password_hash" not in create_body["data"]["user"]

    list_body = admin_api.users(current_user=current_user, session=session)
    _assert_envelope(list_body)
    assert list_body["ok"] is True
    assert all("password_hash" not in user for user in list_body["data"]["users"])

    delete_body = admin_api.delete_user(
        user_id=created_user_id,
        current_user=current_user,
        session=session,
    )
    _assert_envelope(delete_body)
    assert delete_body["ok"] is True
    assert delete_body["data"]["deactivated"] is True


def test_admin_cannot_deactivate_current_authenticated_admin(tmp_path):
    session = _session_for_test(str(tmp_path / "admin_self_delete.db"))
    admin_password = "admin-local-password"
    admin = User(
        email="admin@example.com",
        password_hash=hash_password(admin_password),
        role="admin",
        display_name="Admin",
        is_active=True,
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)

    current_user = AuthSession(username="admin@example.com", role="admin")
    body = admin_api.delete_user(
        user_id=admin.id,
        current_user=current_user,
        session=session,
    )
    _assert_envelope(body)
    assert body["ok"] is False
    assert body["error"]["code"] == "ADMIN_SELF_DELETE_BLOCKED"
