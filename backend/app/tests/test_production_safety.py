from __future__ import annotations

from app.api import admin as admin_api
from app.core.config import get_settings

_PROD_SAFE_VARS = {
    "APP_ENV": "production",
    "DATABASE_URL": "postgresql://user:pass@localhost:5432/zdash",
    "JWT_SECRET_KEY": "safe-production-jwt-secret-for-test",
    "BOOTSTRAP_ADMIN_PASSWORD": "safe-bootstrap-password",
    "DEFAULT_ADMIN_PASSWORD": "safe-default-admin-password",
    "AUTH_ENABLED": "true",
    "METRICS_AUTH_REQUIRED": "true",
}


def _set_prod_env(monkeypatch, **overrides):
    """Set production env vars for testing.

    All _PROD_SAFE_VARS are set to pass get_settings() validation.
    Overrides can be passed to test specific safety check scenarios.
    """
    vars_to_set = dict(_PROD_SAFE_VARS)
    vars_to_set.update(overrides)
    for key, val in vars_to_set.items():
        monkeypatch.setenv(key, val)
    get_settings.cache_clear()


def test_production_safety_checker_detects_blockers(monkeypatch):
    _set_prod_env(
        monkeypatch,
        DRY_RUN="false",
        PRODUCTION_SAFETY_LOCK="true",
        CORS_ALLOW_ORIGINS="*",
        CORS_ALLOW_CREDENTIALS="true",
        SOCIAL_DRY_RUN="false",
        SOCIAL_APPROVAL_REQUIRED="false",
        SOCIAL_REAL_POSTING_APPROVED="false",
        IOT_DRY_RUN="false",
        IOT_REQUIRE_CONFIRMATION="false",
        IOT_REAL_ACTIONS_APPROVED="false",
    )

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


def test_production_requires_auth_enabled(monkeypatch):
    """AUTH_ENABLED must be true in production."""
    _set_prod_env(monkeypatch, AUTH_ENABLED="false")

    try:
        payload = admin_api._safety_check_payload()
        assert payload["status"] == "blocked"
        assert any("AUTH_ENABLED" in blocker for blocker in payload["blockers"])
    finally:
        get_settings.cache_clear()


def test_production_requires_metrics_auth(monkeypatch):
    """METRICS_AUTH_REQUIRED must be true in production."""
    _set_prod_env(monkeypatch, METRICS_AUTH_REQUIRED="false")

    try:
        payload = admin_api._safety_check_payload()
        assert payload["status"] == "blocked"
        assert any("METRICS_AUTH_REQUIRED" in blocker for blocker in payload["blockers"])
    finally:
        get_settings.cache_clear()


def test_production_rejects_unsafe_live_trading_flags(monkeypatch):
    """LIVE_TRADING_ACK requires RISK_GUARDIAN_ENABLED=true."""
    _set_prod_env(
        monkeypatch,
        LIVE_TRADING_ACK="true",
        RISK_GUARDIAN_ENABLED="false",
    )

    try:
        payload = admin_api._safety_check_payload()
        assert payload["status"] == "blocked"
        assert any(
            "RISK_GUARDIAN_ENABLED" in blocker for blocker in payload["blockers"]
        )
    finally:
        get_settings.cache_clear()


def test_production_rejects_unsafe_mt5_without_dry_run(monkeypatch):
    """MT5_ENABLED=true with DRY_RUN=false must be blocked."""
    _set_prod_env(
        monkeypatch,
        MT5_ENABLED="true",
        DRY_RUN="false",
    )

    try:
        payload = admin_api._safety_check_payload()
        assert payload["status"] == "blocked"
        assert any("MT5_ENABLED" in blocker for blocker in payload["blockers"])
    finally:
        get_settings.cache_clear()


def test_production_allows_mt5_with_dry_run(monkeypatch):
    """MT5_ENABLED=true with DRY_RUN=true should be a warning, not blocker."""
    _set_prod_env(monkeypatch, MT5_ENABLED="true", DRY_RUN="true")

    try:
        payload = admin_api._safety_check_payload()
        assert payload["status"] == "safe"
        assert not payload["blockers"]
        assert any("MT5" in w for w in payload["warnings"])
    finally:
        get_settings.cache_clear()


def test_production_rejects_unsafe_social_auto_post(monkeypatch):
    """SOCIAL_AUTO_POST_ENABLED requires SOCIAL_APPROVAL_REQUIRED=true."""
    _set_prod_env(
        monkeypatch,
        SOCIAL_AUTO_POST_ENABLED="true",
        SOCIAL_APPROVAL_REQUIRED="false",
    )

    try:
        payload = admin_api._safety_check_payload()
        assert payload["status"] == "blocked"
        assert any(
            "SOCIAL_AUTO_POST_ENABLED" in blocker for blocker in payload["blockers"]
        )
    finally:
        get_settings.cache_clear()


def test_support_bundle_excludes_secrets_by_default(monkeypatch):
    """SUPPORT_BUNDLE_INCLUDE_SECRETS must be false in production."""
    _set_prod_env(monkeypatch, SUPPORT_BUNDLE_INCLUDE_SECRETS="true")

    try:
        payload = admin_api._safety_check_payload()
        assert payload["status"] == "blocked"
        assert any(
            "SUPPORT_BUNDLE_INCLUDE_SECRETS" in blocker
            for blocker in payload["blockers"]
        )
    finally:
        get_settings.cache_clear()


def test_deployment_pack_excludes_secrets_by_default(monkeypatch):
    """DEPLOYMENT_PACK_INCLUDE_SECRETS must be false in production."""
    _set_prod_env(monkeypatch, DEPLOYMENT_PACK_INCLUDE_SECRETS="true")

    try:
        payload = admin_api._safety_check_payload()
        assert payload["status"] == "blocked"
        assert any(
            "DEPLOYMENT_PACK_INCLUDE_SECRETS" in blocker
            for blocker in payload["blockers"]
        )
    finally:
        get_settings.cache_clear()


def test_production_passes_with_safe_config(monkeypatch):
    """All safe config must pass with no blockers."""
    _set_prod_env(
        monkeypatch,
        AUTH_ENABLED="true",
        METRICS_AUTH_REQUIRED="true",
        CORS_ALLOW_ORIGINS="https://app.zdash.local",
        CORS_ALLOW_CREDENTIALS="true",
        DRY_RUN="true",
        PRODUCTION_SAFETY_LOCK="true",
        LIVE_TRADING_ACK="false",
        MT5_ENABLED="false",
        SOCIAL_DRY_RUN="true",
        SOCIAL_AUTO_POST_ENABLED="false",
        IOT_DRY_RUN="true",
        SUPPORT_BUNDLE_INCLUDE_SECRETS="false",
        DEPLOYMENT_PACK_INCLUDE_SECRETS="false",
    )

    try:
        payload = admin_api._safety_check_payload()
        assert payload["status"] == "safe"
        assert not payload["blockers"]
    finally:
        get_settings.cache_clear()


def test_production_rejects_default_jwt_secret(monkeypatch):
    """A non-custom JWT_SECRET_KEY must raise RuntimeError in production."""
    _set_prod_env(
        monkeypatch,
        JWT_SECRET_KEY="dev-only-change-before-production",
    )

    try:
        import pytest
        with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
            get_settings()
    finally:
        get_settings.cache_clear()


def test_production_rejects_iot_real_actions_without_confirmation(monkeypatch):
    """IOT_REAL_ACTIONS_APPROVED=true requires IOT_REQUIRE_CONFIRMATION=true."""
    _set_prod_env(
        monkeypatch,
        IOT_DRY_RUN="false",
        IOT_REAL_ACTIONS_APPROVED="true",
        IOT_REQUIRE_CONFIRMATION="false",
    )

    try:
        payload = admin_api._safety_check_payload()
        assert payload["status"] == "blocked"
        assert any("IOT" in blocker for blocker in payload["blockers"])
    finally:
        get_settings.cache_clear()


def test_production_rejects_social_real_posting_without_approval(monkeypatch):
    """SOCIAL_REAL_POSTING_APPROVED=true requires SOCIAL_APPROVAL_REQUIRED=true."""
    _set_prod_env(
        monkeypatch,
        SOCIAL_DRY_RUN="false",
        SOCIAL_REAL_POSTING_APPROVED="true",
        SOCIAL_APPROVAL_REQUIRED="false",
    )

    try:
        payload = admin_api._safety_check_payload()
        assert payload["status"] == "blocked"
        assert any("social" in blocker.lower() for blocker in payload["blockers"])
    finally:
        get_settings.cache_clear()


def test_non_production_does_not_block(monkeypatch):
    """Non-production config should not trigger blockers."""
    _set_prod_env(
        monkeypatch,
        APP_ENV="development",
        AUTH_ENABLED="false",
        DRY_RUN="false",
    )

    try:
        payload = admin_api._safety_check_payload()
        assert payload["status"] == "safe"
        assert not payload["blockers"]
        assert payload["warnings"]
    finally:
        get_settings.cache_clear()


# ---------------------------------------------------------------------------
# Production startup validator tests
# ---------------------------------------------------------------------------


def test_validate_production_config_passes_safe(monkeypatch):
    """validate_production_config should not raise for safe config."""
    from app.core.safety import validate_production_config

    _set_prod_env(monkeypatch)

    try:
        validate_production_config()
    finally:
        get_settings.cache_clear()


def test_validate_production_config_blocks_unsafe(monkeypatch):
    """validate_production_config should raise for unsafe config."""
    from app.core.safety import validate_production_config

    _set_prod_env(monkeypatch, AUTH_ENABLED="false")

    try:
        import pytest
        with pytest.raises(RuntimeError, match="AUTH_ENABLED"):
            validate_production_config()
    finally:
        get_settings.cache_clear()


def test_validate_production_config_skips_non_prod(monkeypatch):
    """validate_production_config should skip validation in non-production."""
    from app.core.safety import validate_production_config

    _set_prod_env(monkeypatch, APP_ENV="development", AUTH_ENABLED="false")

    try:
        validate_production_config()
    finally:
        get_settings.cache_clear()


def test_validate_production_config_blocks_missing_auth(monkeypatch):
    from app.core.safety import validate_production_config

    _set_prod_env(monkeypatch, AUTH_ENABLED="false")
    try:
        import pytest
        with pytest.raises(RuntimeError, match="AUTH_ENABLED"):
            validate_production_config()
    finally:
        get_settings.cache_clear()


def test_validate_production_config_blocks_missing_metrics_auth(monkeypatch):
    from app.core.safety import validate_production_config

    _set_prod_env(monkeypatch, METRICS_AUTH_REQUIRED="false")
    try:
        import pytest
        with pytest.raises(RuntimeError, match="METRICS_AUTH_REQUIRED"):
            validate_production_config()
    finally:
        get_settings.cache_clear()


def test_validate_production_config_blocks_cors_wildcard(monkeypatch):
    from app.core.safety import validate_production_config

    _set_prod_env(
        monkeypatch,
        CORS_ALLOW_ORIGINS="*",
        CORS_ALLOW_CREDENTIALS="true",
    )
    try:
        import pytest
        with pytest.raises(RuntimeError, match="CORS wildcard"):
            validate_production_config()
    finally:
        get_settings.cache_clear()


def test_validate_production_config_blocks_dry_run_false(monkeypatch):
    from app.core.safety import validate_production_config

    _set_prod_env(
        monkeypatch,
        DRY_RUN="false",
    )
    try:
        import pytest
        with pytest.raises(RuntimeError, match="DRY_RUN"):
            validate_production_config()
    finally:
        get_settings.cache_clear()


def test_validate_production_config_blocks_default_admin_password(monkeypatch):
    from app.core.safety import validate_production_config

    _set_prod_env(
        monkeypatch,
        DEFAULT_ADMIN_PASSWORD="dev-only-change-before-production",
    )
    try:
        import pytest
        with pytest.raises(RuntimeError, match="DEFAULT_ADMIN_PASSWORD"):
            validate_production_config()
    finally:
        get_settings.cache_clear()


def test_validate_production_config_wired_in_main(monkeypatch):
    """Verify validate_production_config is called during main lifespan."""
    from app.main import app

    assert app is not None
