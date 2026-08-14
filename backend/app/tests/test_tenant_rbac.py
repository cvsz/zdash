"""Tests for tenant-level RBAC functionality."""
import pytest

from app.auth.rbac import Permission, RoleName, has_permission, normalize_role
from app.tenancy.tenant_context import TenantContext


@pytest.fixture
def admin_context() -> TenantContext:
    """Create an admin tenant context."""
    return TenantContext(
        organization_id="test_org",
        workspace_id="test_ws",
        user_id="admin_user",
        user_role="admin",
    )


@pytest.fixture
def operator_context() -> TenantContext:
    """Create an operator tenant context."""
    return TenantContext(
        organization_id="test_org",
        workspace_id="test_ws",
        user_id="operator_user",
        user_role="operator",
    )


@pytest.fixture
def analyst_context() -> TenantContext:
    """Create an analyst tenant context."""
    return TenantContext(
        organization_id="test_org",
        workspace_id="test_ws",
        user_id="analyst_user",
        user_role="analyst",
    )


@pytest.fixture
def viewer_context() -> TenantContext:
    """Create a viewer tenant context."""
    return TenantContext(
        organization_id="test_org",
        workspace_id="test_ws",
        user_id="viewer_user",
        user_role="viewer",
    )


def test_normalize_role_valid_roles() -> None:
    """Test role normalization with valid roles."""
    assert normalize_role("admin") == "admin"
    assert normalize_role("operator") == "operator"
    assert normalize_role("analyst") == "analyst"
    assert normalize_role("viewer") == "viewer"


def test_normalize_role_invalid_role() -> None:
    """Test role normalization defaults to viewer for unknown roles."""
    assert normalize_role("unknown_role") == "viewer"
    assert normalize_role("") == "viewer"


def test_admin_has_all_permissions(admin_context: TenantContext) -> None:
    """Test that admin role has all permissions."""
    for permission in Permission:
        assert has_permission(admin_context.user_role, permission) is True


def test_operator_can_manage_workers(operator_context: TenantContext) -> None:
    """Test operator can manage workers and notifications."""
    assert has_permission(operator_context.user_role, Permission.MANAGE_WORKERS) is True
    assert (
        has_permission(operator_context.user_role, Permission.MANAGE_NOTIFICATIONS)
        is True
    )
    assert has_permission(operator_context.user_role, Permission.READ_LOGS) is False


def test_analyst_can_read_but_not_manage(analyst_context: TenantContext) -> None:
    """Test analyst has read-only permissions."""
    assert has_permission(analyst_context.user_role, Permission.READ_DASHBOARD) is True
    assert has_permission(analyst_context.user_role, Permission.RUN_BACKTESTS) is True
    assert has_permission(analyst_context.user_role, Permission.READ_LOGS) is True
    assert (
        has_permission(analyst_context.user_role, Permission.MANAGE_CONTENT_APPROVAL)
        is False
    )
    assert (
        has_permission(analyst_context.user_role, Permission.MANAGE_WORKERS) is False
    )


def test_viewer_limited_access(viewer_context: TenantContext) -> None:
    """Test viewer has minimal read-only access."""
    assert has_permission(viewer_context.user_role, Permission.READ_DASHBOARD) is True
    assert has_permission(viewer_context.user_role, Permission.READ_TENANCY) is True
    assert has_permission(viewer_context.user_role, Permission.RUN_BACKTESTS) is False
    assert has_permission(viewer_context.user_role, Permission.READ_LOGS) is False


def test_billing_permissions_by_role() -> None:
    """Test billing-related permissions across roles."""
    assert has_permission("admin", Permission.billing_read) is True
    assert has_permission("admin", Permission.billing_manage) is True
    assert has_permission("operator", Permission.billing_read) is True
    assert has_permission("operator", Permission.billing_manage) is False
    assert has_permission("analyst", Permission.billing_read) is True
    assert has_permission("viewer", Permission.billing_read) is True


def test_marketplace_permissions_by_role() -> None:
    """Test marketplace permissions across roles."""
    assert has_permission("admin", Permission.marketplace_manage) is True
    assert has_permission("admin", Permission.marketplace_install) is True
    assert has_permission("operator", Permission.marketplace_install) is True
    assert has_permission("operator", Permission.marketplace_manage) is False
    assert has_permission("analyst", Permission.marketplace_read) is True
    assert has_permission("analyst", Permission.marketplace_install) is False
    assert has_permission("viewer", Permission.marketplace_read) is True


def test_team_permissions_by_role() -> None:
    """Test team management permissions across roles."""
    assert has_permission("admin", Permission.team_manage) is True
    assert has_permission("admin", Permission.team_invite) is True
    assert has_permission("operator", Permission.team_manage) is True
    assert has_permission("operator", Permission.team_invite) is True
    assert has_permission("analyst", Permission.team_read) is True
    assert has_permission("analyst", Permission.team_manage) is False
    assert has_permission("viewer", Permission.team_read) is False
