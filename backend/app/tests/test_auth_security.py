from __future__ import annotations

import pytest

from app.auth.jwt import create_access_token, decode_token
from app.auth.models import AuthSession
from app.auth.password import hash_password, verify_password
from app.auth.rbac import Permission, has_permission
from app.core.config import get_settings


class TestAuthSecurity:
    def test_password_hashing_roundtrip(self) -> None:
        candidate = "test-" + "credential-123"
        hashed = hash_password(candidate)
        assert verify_password(candidate, hashed) is True

    def test_password_hashing_wrong_password(self) -> None:
        hashed = hash_password("correct-password")
        assert verify_password("wrong-password", hashed) is False

    def test_jwt_token_creation_and_decoding(self) -> None:
        token = create_access_token(sub="test-user", role="admin")
        payload = decode_token(token)
        assert payload["sub"] == "test-user"
        assert payload["role"] == "admin"

    def test_jwt_token_expired(self) -> None:
        token = create_access_token(sub="test-user", role="admin")
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "test-user"

    def test_has_permission_admin(self) -> None:
        assert has_permission("admin", Permission.enterprise_read) is True
        assert has_permission("admin", Permission.enterprise_license_manage) is True
        assert has_permission("admin", Permission.enterprise_export_secrets) is True

    def test_has_permission_viewer_restricted(self) -> None:
        assert has_permission("viewer", Permission.enterprise_read) is True
        assert has_permission("viewer", Permission.enterprise_license_manage) is False
        assert has_permission("viewer", Permission.enterprise_export) is False

    def test_auth_session_creation(self) -> None:
        session = AuthSession(username="test-user", role="admin")
        assert session.username == "test-user"
        assert session.role == "admin"

    def test_auth_session_viewer_default(self) -> None:
        session = AuthSession(username="viewer-user", role="viewer")
        assert session.role == "viewer"

    @pytest.mark.parametrize(
        ("role", "perm", "expected"),
        [
            ("admin", Permission.enterprise_read, True),
            ("admin", Permission.enterprise_export_secrets, True),
            ("admin", Permission.enterprise_license_manage, True),
            ("viewer", Permission.enterprise_read, True),
            ("viewer", Permission.enterprise_export_secrets, False),
            ("viewer", Permission.enterprise_license_manage, False),
            ("operator", Permission.READ_LOGS, False),
            ("operator", Permission.enterprise_export_secrets, False),
        ],
    )
    def test_rbac_matrix(self, role: str, perm: Permission, expected: bool) -> None:
        assert has_permission(role, perm) is expected

    def test_production_safety_lock_default_true(self) -> None:
        settings = get_settings()
        assert settings.production_safety_lock is True

    def test_dry_run_default_true(self) -> None:
        settings = get_settings()
        assert settings.dry_run is True

    def test_live_trading_ack_default_false(self) -> None:
        settings = get_settings()
        assert settings.live_trading_ack is False
