from __future__ import annotations

from app.api import admin as admin_api
from app.core.config import get_settings


def test_production_safety_checker_detects_blockers(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/zdash")
    monkeypatch.setenv("DRY_RUN", "false")
    monkeypatch.setenv("PRODUCTION_SAFETY_LOCK", "true")
    monkeypatch.setenv("JWT_SECRET_KEY", "safe-production-jwt-secret")
    monkeypatch.setenv("BOOTSTRAP_ADMIN_PASSWORD", "safe-bootstrap-password")
    monkeypatch.setenv("DEFAULT_ADMIN_PASSWORD", "safe-default-admin-password")
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", "*")
    monkeypatch.setenv("CORS_ALLOW_CREDENTIALS", "true")
    monkeypatch.setenv("SOCIAL_DRY_RUN", "false")
    monkeypatch.setenv("SOCIAL_APPROVAL_REQUIRED", "false")
    monkeypatch.setenv("SOCIAL_REAL_POSTING_APPROVED", "false")
    monkeypatch.setenv("IOT_DRY_RUN", "false")
    monkeypatch.setenv("IOT_REQUIRE_CONFIRMATION", "false")
    monkeypatch.setenv("IOT_REAL_ACTIONS_APPROVED", "false")
    get_settings.cache_clear()

    try:
        payload = admin_api._safety_check_payload()
        assert payload["status"] == "blocked"
        assert payload["blockers"]
        assert any("DRY_RUN" in blocker for blocker in payload["blockers"])
        assert not any("JWT_SECRET_KEY" in blocker for blocker in payload["blockers"])
        assert not any(
            "DEFAULT_ADMIN_PASSWORD" in blocker for blocker in payload["blockers"]
        )
        assert any("CORS wildcard" in blocker for blocker in payload["blockers"])
    finally:
        get_settings.cache_clear()
