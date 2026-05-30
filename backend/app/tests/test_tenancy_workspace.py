from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.api import tenancy
from app.auth.models import AuthSession
from app.tenancy.models import (
    MemberCreateRequest,
    OrganizationCreateRequest,
    OrganizationUpdateRequest,
    WorkspaceCreateRequest,
    WorkspaceUpdateRequest,
)


@pytest.fixture(autouse=True)
def tenant_guards():
    mock_service = MagicMock()
    mock_org = MagicMock()
    mock_org.id = "org-1"
    mock_org.name = "Test Org"
    mock_org.model_dump.return_value = {
        "id": "org-1",
        "name": "Test Org",
        "created_at": "2026-01-01T00:00:00",
    }
    mock_ws = MagicMock()
    mock_ws.id = "ws-1"
    mock_ws.name = "Test Workspace"
    mock_ws.organization_id = "org-1"
    mock_ws.model_dump.return_value = {
        "id": "ws-1",
        "name": "Test Workspace",
        "organization_id": "org-1",
    }
    mock_member = MagicMock()
    mock_member.model_dump.return_value = {
        "user_id": "user-1",
        "role": "member",
        "organization_id": "org-1",
    }

    mock_service.list_accessible_organizations.return_value = [mock_org]
    mock_service.get_organization.return_value = mock_org
    mock_service.create_organization.return_value = mock_org
    mock_service.update_organization.return_value = mock_org
    mock_service.list_workspaces.return_value = [mock_ws]
    mock_service.get_workspace.return_value = mock_ws
    mock_service.create_workspace.return_value = mock_ws
    mock_service.update_workspace.return_value = mock_ws
    mock_service.is_organization_admin.return_value = True
    mock_service.can_access_workspace.return_value = True
    mock_service.add_organization_member.return_value = mock_member
    mock_service.add_workspace_member.return_value = mock_member

    with (
        patch("app.api.tenancy.tenant_service", mock_service),
        patch("app.api.tenancy.event_bus.emit"),
    ):
        yield


def _admin() -> AuthSession:
    return AuthSession(username="tenancy-admin", role="admin")


def test_context_endpoint() -> None:
    mock_ctx_obj = MagicMock(spec=object)
    mock_ctx_obj.__dict__ = {"organization_id": "org-1", "workspace_id": "ws-1"}
    result = tenancy.context(tenant_context=mock_ctx_obj)
    assert result["ok"] is True
    assert result["data"]["context"]["organization_id"] == "org-1"


def test_organizations_list() -> None:
    result = tenancy.organizations(user=_admin())
    assert result["ok"] is True
    assert len(result["data"]["items"]) >= 1
    assert result["data"]["items"][0]["name"] == "Test Org"


def test_create_organization() -> None:
    payload = OrganizationCreateRequest(
        name="New Org",
        slug="new-org",
    )
    result = tenancy.create_organization(payload, user=_admin())
    assert result["ok"] is True
    assert result["data"]["item"]["name"] == "Test Org"


def test_get_organization() -> None:
    result = tenancy.get_organization("org-1", user=_admin())
    assert result["ok"] is True
    assert result["data"]["item"]["id"] == "org-1"


def test_update_organization() -> None:
    payload = OrganizationUpdateRequest(name="Updated Org")
    result = tenancy.patch_organization("org-1", payload, user=_admin())
    assert result["ok"] is True
    assert result["data"]["item"]["name"] == "Test Org"


def test_list_workspaces() -> None:
    result = tenancy.list_workspaces("org-1", user=_admin())
    assert result["ok"] is True
    assert len(result["data"]["items"]) == 1


def test_create_workspace() -> None:
    payload = WorkspaceCreateRequest(
        name="New Workspace",
        slug="new-ws",
    )
    result = tenancy.create_workspace("org-1", payload, user=_admin())
    assert result["ok"] is True


def test_get_workspace() -> None:
    result = tenancy.get_workspace("ws-1", user=_admin())
    assert result["ok"] is True
    assert result["data"]["item"]["id"] == "ws-1"


def test_update_workspace() -> None:
    payload = WorkspaceUpdateRequest(name="Updated Workspace")
    result = tenancy.patch_workspace("ws-1", payload, user=_admin())
    assert result["ok"] is True


def test_add_organization_member() -> None:
    payload = MemberCreateRequest(user_id="user-2", role="viewer")
    result = tenancy.add_organization_member("org-1", payload, user=_admin())
    assert result["ok"] is True


def test_add_workspace_member() -> None:
    payload = MemberCreateRequest(user_id="user-2", role="viewer")
    result = tenancy.add_workspace_member("ws-1", payload, user=_admin())
    assert result["ok"] is True
