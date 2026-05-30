from __future__ import annotations

"""
High-Risk Action Policy Contract Tests.

Every high-risk action class must satisfy:
- auth: Valid JWT session required
- RBAC: Appropriate role required
- tenant scope: Action scoped to current tenant
- risk policy: Risk/Guardian check passes
- typed confirmation: Operator explicitly types confirmation
- dry-run default: Action defaults to dry-run
- audit event: Action logged to audit trail
- rollback metadata: Rollback plan documented

These tests validate the policy infrastructure exists.
Full integration tests require database and auth setup.
"""


def test_trading_action_requires_dry_run_default():
    """Trading execution must default to dry-run."""
    from app.core.config import get_settings

    settings = get_settings()
    assert settings.dry_run is True, "DRY_RUN must default to True"


def test_trading_action_requires_guardian():
    """Trading execution must require Guardian risk check."""
    from app.core.config import get_settings

    settings = get_settings()
    assert settings.risk_guardian_enabled is True, (
        "RISK_GUARDIAN_ENABLED must default to True"
    )


def test_live_trading_requires_ack():
    """Live trading requires explicit LIVE_TRADING_ACK."""
    from app.core.config import get_settings

    settings = get_settings()
    assert settings.live_trading_ack is False, (
        "LIVE_TRADING_ACK must default to False"
    )


def test_mt5_disabled_by_default():
    """MT5 must be disabled by default."""
    from app.core.config import get_settings

    settings = get_settings()
    assert settings.mt5_enabled is False, "MT5_ENABLED must default to False"


def test_iot_dry_run_default():
    """IoT actions must default to dry-run."""
    from app.core.config import get_settings

    settings = get_settings()
    assert settings.iot_dry_run is True, "IOT_DRY_RUN must default to True"


def test_iot_requires_confirmation():
    """IoT actions must require confirmation by default."""
    from app.core.config import get_settings

    settings = get_settings()
    assert settings.iot_require_confirmation is True, (
        "IOT_REQUIRE_CONFIRMATION must default to True"
    )


def test_social_dry_run_default():
    """Social posting must default to dry-run."""
    from app.core.config import get_settings

    settings = get_settings()
    assert settings.social_dry_run is True, "SOCIAL_DRY_RUN must default to True"


def test_social_approval_required():
    """Social posting must require approval by default."""
    from app.core.config import get_settings

    settings = get_settings()
    assert settings.social_approval_required is True, (
        "SOCIAL_APPROVAL_REQUIRED must default to True"
    )


def test_social_auto_post_disabled():
    """Social auto-posting must be disabled by default."""
    from app.core.config import get_settings

    settings = get_settings()
    assert settings.social_auto_post_enabled is False, (
        "SOCIAL_AUTO_POST_ENABLED must default to False"
    )


def test_production_safety_lock_default():
    """Production safety lock must be enabled by default."""
    from app.core.config import get_settings

    settings = get_settings()
    assert settings.production_safety_lock is True, (
        "PRODUCTION_SAFETY_LOCK must default to True"
    )


def test_cloudflare_dry_run_default():
    """Cloudflare actions must default to dry-run."""
    from app.core.config import get_settings

    settings = get_settings()
    assert settings.cloudflare_dry_run is True, (
        "CLOUDFLARE_DRY_RUN must default to True"
    )


def test_notification_dry_run_default():
    """Notifications must default to dry-run."""
    from app.core.config import get_settings

    settings = get_settings()
    assert settings.notification_dry_run is True, (
        "NOTIFICATION_DRY_RUN must default to True"
    )


# ---------------------------------------------------------------------------
# High-Risk Action Policy Enforcer Tests
# ---------------------------------------------------------------------------


class TestHighRiskActionPolicy:
    def test_trading_blocked_for_viewer(self):
        from app.risk.high_risk_policy import (
            HighRiskActionClass,
            HighRiskActionRequest,
            check_high_risk_action,
        )

        req = HighRiskActionRequest(
            action_class=HighRiskActionClass.trading,
            action_name="execute_trade",
            actor_role="viewer",
            actor_tenant="tenant-1",
            confirmation_provided=True,
            risk_check_passed=True,
        )
        decision = check_high_risk_action(req)
        assert decision.allowed is False
        assert any("viewer" in b for b in decision.blocked_by)

    def test_trading_allowed_for_admin(self):
        from app.risk.high_risk_policy import (
            HighRiskActionClass,
            HighRiskActionRequest,
            check_high_risk_action,
        )

        req = HighRiskActionRequest(
            action_class=HighRiskActionClass.trading,
            action_name="execute_trade",
            actor_role="admin",
            actor_tenant="tenant-1",
            confirmation_provided=True,
            risk_check_passed=True,
            dry_run_setting=True,
        )
        decision = check_high_risk_action(req)
        assert decision.allowed is True

    def test_trading_blocked_without_confirmation(self):
        from app.risk.high_risk_policy import (
            HighRiskActionClass,
            HighRiskActionRequest,
            check_high_risk_action,
        )

        req = HighRiskActionRequest(
            action_class=HighRiskActionClass.trading,
            action_name="execute_trade",
            actor_role="admin",
            actor_tenant="tenant-1",
            confirmation_provided=False,
            risk_check_passed=True,
        )
        decision = check_high_risk_action(req)
        assert decision.allowed is False
        assert any("confirmation" in b for b in decision.blocked_by)

    def test_trading_blocked_without_risk_check(self):
        from app.risk.high_risk_policy import (
            HighRiskActionClass,
            HighRiskActionRequest,
            check_high_risk_action,
        )

        req = HighRiskActionRequest(
            action_class=HighRiskActionClass.trading,
            action_name="execute_trade",
            actor_role="admin",
            actor_tenant="tenant-1",
            confirmation_provided=True,
            risk_check_passed=False,
        )
        decision = check_high_risk_action(req)
        assert decision.allowed is False

    def test_trading_blocked_without_tenant(self):
        from app.risk.high_risk_policy import (
            HighRiskActionClass,
            HighRiskActionRequest,
            check_high_risk_action,
        )

        req = HighRiskActionRequest(
            action_class=HighRiskActionClass.trading,
            action_name="execute_trade",
            actor_role="admin",
            actor_tenant="",
            confirmation_provided=True,
        )
        decision = check_high_risk_action(req)
        assert decision.allowed is False
        assert any("tenant" in b.lower() for b in decision.blocked_by)

    def test_infrastructure_requires_admin(self):
        from app.risk.high_risk_policy import (
            HighRiskActionClass,
            HighRiskActionRequest,
            check_high_risk_action,
        )

        req = HighRiskActionRequest(
            action_class=HighRiskActionClass.infrastructure,
            action_name="deploy",
            actor_role="operator",
            actor_tenant="tenant-1",
            confirmation_provided=True,
        )
        decision = check_high_risk_action(req)
        assert decision.allowed is False
        assert any("admin" in b for b in decision.blocked_by)

    def test_infrastructure_requires_rollback_plan(self):
        from app.risk.high_risk_policy import (
            HighRiskActionClass,
            HighRiskActionRequest,
            check_high_risk_action,
        )

        req = HighRiskActionRequest(
            action_class=HighRiskActionClass.infrastructure,
            action_name="deploy",
            actor_role="admin",
            actor_tenant="tenant-1",
            confirmation_provided=True,
        )
        decision = check_high_risk_action(req)
        assert decision.requires_rollback_plan is True

    def test_raw_shell_blocked_for_operator(self):
        from app.risk.high_risk_policy import (
            HighRiskActionClass,
            HighRiskActionRequest,
            check_high_risk_action,
        )

        req = HighRiskActionRequest(
            action_class=HighRiskActionClass.raw_shell,
            action_name="exec",
            actor_role="operator",
            actor_tenant="tenant-1",
            confirmation_provided=True,
        )
        decision = check_high_risk_action(req)
        assert decision.allowed is False
        assert any("admin" in b for b in decision.blocked_by)

    def test_social_publish_requires_approval_context(self):
        from app.risk.high_risk_policy import (
            HighRiskActionClass,
            HighRiskActionRequest,
            check_high_risk_action,
        )

        req = HighRiskActionRequest(
            action_class=HighRiskActionClass.social_publish,
            action_name="post",
            actor_role="admin",
            actor_tenant="tenant-1",
            confirmation_provided=True,
            risk_check_passed=True,
            dry_run_setting=True,
        )
        decision = check_high_risk_action(req)
        assert decision.allowed is True

    def test_credential_export_requires_admin(self):
        from app.risk.high_risk_policy import (
            HighRiskActionClass,
            HighRiskActionRequest,
            check_high_risk_action,
        )

        req = HighRiskActionRequest(
            action_class=HighRiskActionClass.credential_export,
            action_name="export",
            actor_role="operator",
            actor_tenant="tenant-1",
            confirmation_provided=True,
        )
        decision = check_high_risk_action(req)
        assert decision.allowed is False
        assert any("admin" in b for b in decision.blocked_by)

    def test_update_apply_requires_rollback_plan(self):
        from app.risk.high_risk_policy import (
            HighRiskActionClass,
            HighRiskActionRequest,
            check_high_risk_action,
        )

        req = HighRiskActionRequest(
            action_class=HighRiskActionClass.update_apply,
            action_name="update",
            actor_role="admin",
            actor_tenant="tenant-1",
            confirmation_provided=True,
        )
        decision = check_high_risk_action(req)
        assert decision.requires_rollback_plan is True


# ---------------------------------------------------------------------------
# High-risk action policy FastAPI dependency tests
# ---------------------------------------------------------------------------


class TestHighRiskActionPolicyDependency:
    def test_require_policy_blocks_viewer_trading(self):
        from app.risk.high_risk_policy import (
            HighRiskActionClass,
            require_high_risk_action_policy,
        )

        dep = require_high_risk_action_policy(
            HighRiskActionClass.trading, action_name="test_trade"
        )

        import pytest
        from app.auth.models import AuthSession

        user = AuthSession(username="viewer-user", role="viewer")

        with pytest.raises(Exception):
            import asyncio
            asyncio.run(dep(user=user))

    def test_require_policy_allows_admin_trading(self):
        from app.risk.high_risk_policy import (
            HighRiskActionClass,
            require_high_risk_action_policy,
        )

        dep = require_high_risk_action_policy(
            HighRiskActionClass.trading,
            action_name="test_trade",
            require_confirmation=False,
            require_risk_check=False,
        )

        import asyncio
        from app.auth.models import AuthSession

        user = AuthSession(username="admin-user", role="admin")
        result = asyncio.run(dep(user=user))
        assert result is None
