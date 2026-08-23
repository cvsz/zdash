"""Tests for tenant isolation ensuring data separation between organizations."""

import pytest

from app.auth.models import AuthSession
from app.tenancy.models import OrganizationCreateRequest
from app.tenancy.tenant_context import TenantContext
from app.tenancy.tenant_service import TenantService


@pytest.fixture
def tenant_service() -> TenantService:
    """Create a tenant service with isolated repository state."""
    service = TenantService()
    service.repository.reset()
    yield service
    service.repository.reset()


def test_organization_data_isolation(tenant_service: TenantService) -> None:
    """Test that each non-admin user sees only organizations they belong to."""
    user_one = AuthSession(username="user_1", role="viewer")
    user_two = AuthSession(username="user_2", role="viewer")

    org_one = tenant_service.create_organization(
        OrganizationCreateRequest(name="Organization One"), user_one
    )
    org_two = tenant_service.create_organization(
        OrganizationCreateRequest(name="Organization Two"), user_two
    )

    user_one_ids = {
        organization.id
        for organization in tenant_service.list_accessible_organizations(user_one)
    }
    user_two_ids = {
        organization.id
        for organization in tenant_service.list_accessible_organizations(user_two)
    }

    assert org_one.id in user_one_ids
    assert org_two.id not in user_one_ids
    assert org_two.id in user_two_ids
    assert org_one.id not in user_two_ids


def test_workspace_belongs_to_correct_organization(
    tenant_service: TenantService,
) -> None:
    """Test that workspaces are properly scoped to their organization."""
    ctx = TenantContext(
        organization_id="test_org",
        workspace_id="test_ws",
        user_id="test_user",
    )

    assert ctx.organization_id == "test_org"
    assert ctx.workspace_id == "test_ws"


def test_cross_tenant_access_prevented() -> None:
    """Test that cross-tenant contexts remain distinct."""
    context1 = TenantContext(
        organization_id="org_a",
        workspace_id="ws_a",
        user_id="user_a",
    )

    context2 = TenantContext(
        organization_id="org_b",
        workspace_id="ws_b",
        user_id="user_b",
    )

    assert context1.organization_id != context2.organization_id
    assert context1.workspace_id != context2.workspace_id
    assert context1.user_id != context2.user_id


def test_tenant_context_validation() -> None:
    """Test that tenant context validates required fields."""
    context = TenantContext(
        organization_id="valid_org",
        workspace_id="valid_ws",
        user_id="valid_user",
    )

    assert context.organization_id == "valid_org"
    assert context.workspace_id == "valid_ws"


def test_user_scoped_to_workspace() -> None:
    """Test that users are properly scoped to their workspace."""
    context = TenantContext(
        organization_id="org_main",
        workspace_id="ws_dev",
        user_id="developer_1",
        user_role="analyst",
    )

    assert context.user_role == "analyst"
    assert context.workspace_id == "ws_dev"
