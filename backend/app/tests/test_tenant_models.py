"""Tests for tenant models (Organization, Workspace, Membership)."""

import pytest

from app.tenancy.models import (
    MemberCreateRequest,
    Organization,
    OrganizationCreateRequest,
    Workspace,
    WorkspaceCreateRequest,
)


@pytest.fixture
def sample_org_data() -> dict:
    """Sample organization data."""
    return {
        "name": "Test Organization",
        "slug": "test-org",
        "description": "A test organization",
    }


@pytest.fixture
def sample_workspace_data() -> dict:
    """Sample workspace data."""
    return {
        "name": "Test Workspace",
        "slug": "test-workspace",
        "description": "A test workspace",
    }


def test_create_organization_request() -> None:
    """Test creating an organization request validates correctly."""
    payload = OrganizationCreateRequest(
        name="My Org",
        slug="my-org",
    )

    assert payload.name == "My Org"
    assert payload.slug == "my-org"


def test_organization_model_creation(sample_org_data: dict) -> None:
    """Test creating an Organization model."""
    org = Organization(
        id="org_123",
        name=sample_org_data["name"],
        slug=sample_org_data["slug"],
        owner_user_id="owner_123",
    )

    assert org.id == "org_123"
    assert org.name == sample_org_data["name"]
    assert org.slug == sample_org_data["slug"]
    assert org.status == "active"


def test_workspace_model_creation(sample_workspace_data: dict) -> None:
    """Test creating a Workspace model."""
    workspace = Workspace(
        id="ws_456",
        organization_id="org_123",
        name=sample_workspace_data["name"],
        slug=sample_workspace_data["slug"],
    )

    assert workspace.id == "ws_456"
    assert workspace.organization_id == "org_123"
    assert workspace.name == sample_workspace_data["name"]
    assert workspace.status == "active"


def test_member_create_request() -> None:
    """Test creating a member request validates correctly."""
    payload = MemberCreateRequest(
        user_id="user_789",
        role="analyst",
    )

    assert payload.user_id == "user_789"
    assert payload.role == "analyst"


def test_organization_slug_generation() -> None:
    """Test that organization slug can be auto-generated."""
    payload = OrganizationCreateRequest(name="Test Organization")

    assert payload.name == "Test Organization"


def test_workspace_belongs_to_organization() -> None:
    """Test workspace has proper organization reference."""
    org = Organization(
        id="org_parent",
        name="Parent Org",
        slug="parent-org",
        owner_user_id="owner_123",
    )
    workspace = Workspace(
        id="ws_child",
        organization_id=org.id,
        name="Child Workspace",
        slug="child-ws",
    )

    assert workspace.organization_id == org.id
