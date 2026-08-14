"""Tests for Phase 9/10 tenancy and enterprise API endpoints."""
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the API."""
    return TestClient(app)


@pytest.fixture
def mock_auth_session() -> MagicMock:
    """Create a mock auth session."""
    mock = MagicMock()
    mock.user_id = "test_user"
    mock.username = "test@example.com"
    mock.role = "admin"
    return mock


@pytest.fixture
def mock_tenant_context() -> MagicMock:
    """Create a mock tenant context."""
    mock = MagicMock()
    mock.organization_id = "test_org"
    mock.workspace_id = "test_ws"
    mock.user_id = "test_user"
    mock.user_role = "admin"
    return mock


def test_get_tenancy_context(
    client: TestClient,
    mock_auth_session: MagicMock,
    mock_tenant_context: MagicMock,
) -> None:
    """Test getting tenant context from API."""
    with patch(
        "app.api.tenancy.get_current_user", return_value=mock_auth_session
    ), patch(
        "app.api.tenancy.get_tenant_context", return_value=mock_tenant_context
    ):
        response = client.get("/api/tenancy/context")

        assert response.status_code == 200
        data = response.json()
        assert "context" in data["data"]


def test_list_organizations(
    client: TestClient,
    mock_auth_session: MagicMock,
) -> None:
    """Test listing organizations accessible to user."""
    mock_org = MagicMock()
    mock_org.id = "org_123"
    mock_org.name = "Test Organization"
    mock_org.model_dump.return_value = {"id": "org_123", "name": "Test Organization"}

    with patch(
        "app.api.tenancy.get_current_user", return_value=mock_auth_session
    ), patch(
        "app.api.tenancy.tenant_service.list_accessible_organizations",
        return_value=[mock_org],
    ):
        response = client.get("/api/tenancy/organizations")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data["data"]
        assert len(data["data"]["items"]) == 1


def test_create_organization(
    client: TestClient,
    mock_auth_session: MagicMock,
) -> None:
    """Test creating a new organization."""
    mock_org = MagicMock()
    mock_org.id = "org_456"
    mock_org.name = "New Organization"
    mock_org.model_dump.return_value = {"id": "org_456", "name": "New Organization"}

    with patch(
        "app.api.tenancy.get_current_user", return_value=mock_auth_session
    ), patch(
        "app.api.tenancy.tenant_service.create_organization", return_value=mock_org
    ), patch("app.api.tenancy._audit"):
        response = client.post(
            "/api/tenancy/organizations",
            json={"name": "New Organization"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "item" in data["data"]
        assert data["data"]["item"]["id"] == "org_456"


def test_get_organization_not_found(
    client: TestClient,
    mock_auth_session: MagicMock,
) -> None:
    """Test getting a non-existent organization."""
    with patch(
        "app.api.tenancy.get_current_user", return_value=mock_auth_session
    ), patch(
        "app.api.tenancy.tenant_service.get_organization", return_value=None
    ):
        response = client.get("/api/tenancy/organizations/nonexistent")

        assert response.status_code == 404


def test_get_organization_access_denied(
    client: TestClient,
    mock_auth_session: MagicMock,
) -> None:
    """Test accessing organization without permission."""
    mock_org = MagicMock()
    mock_org.id = "org_789"

    with patch(
        "app.api.tenancy.get_current_user", return_value=mock_auth_session
    ), patch(
        "app.api.tenancy.tenant_service.get_organization", return_value=mock_org
    ), patch(
        "app.api.tenancy.tenant_service.is_organization_admin", return_value=False
    ), patch(
        "app.api.tenancy.tenant_service.list_accessible_organizations", return_value=[]
    ):
        # Set user role to non-admin to trigger access check
        mock_auth_session.role = "viewer"

        response = client.get("/api/tenancy/organizations/org_789")

        assert response.status_code == 403


def test_create_workspace(
    client: TestClient,
    mock_auth_session: MagicMock,
) -> None:
    """Test creating a new workspace."""
    mock_workspace = MagicMock()
    mock_workspace.id = "ws_123"
    mock_workspace.name = "Test Workspace"
    mock_workspace.model_dump.return_value = {
        "id": "ws_123",
        "name": "Test Workspace",
    }

    with patch(
        "app.api.tenancy.get_current_user", return_value=mock_auth_session
    ), patch(
        "app.api.tenancy.tenant_service.create_workspace", return_value=mock_workspace
    ), patch("app.api.tenancy._audit"):
        response = client.post(
            "/api/tenancy/organizations/org_123/workspaces",
            json={"name": "Test Workspace"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "item" in data["data"]
        assert data["data"]["item"]["id"] == "ws_123"
