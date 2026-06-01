from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.auth.models import AuthSession
from app.main import app


@pytest.fixture(autouse=True)
def mock_auth():
    """Override auth so all endpoints run as admin (permission checks pass)."""
    from app.auth.dependencies import get_current_user

    app.dependency_overrides[get_current_user] = lambda: AuthSession(
        username="admin@zeaz.dev", role="admin"
    )
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def client():
    return TestClient(app)


def _assert_envelope(res: dict) -> None:
    assert "ok" in res
    assert "data" in res
    assert "error" in res
    assert "timestamp" in res


# ---------------------------------------------------------------------------
# GET /api/team/members
# ---------------------------------------------------------------------------


def test_list_members_returns_envelope(client):
    with patch("app.api.team.list_members") as mock_fn:
        mock_fn.return_value = {"ok": True, "members": []}
        res = client.get("/api/team/members")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is True
    assert "members" in res.json()["data"]


def test_list_members_returns_error_envelope(client):
    with patch("app.api.team.list_members") as mock_fn:
        mock_fn.side_effect = RuntimeError("boom")
        res = client.get("/api/team/members")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is False


# ---------------------------------------------------------------------------
# GET /api/team/members/{member_id}
# ---------------------------------------------------------------------------


def test_get_member_returns_envelope(client):
    with patch("app.api.team.get_member") as mock_fn:
        mock_fn.return_value = {
            "ok": True,
            "member": {"id": "m-1", "email": "a@test.com", "role": "viewer"},
        }
        res = client.get("/api/team/members/m-1")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is True
    assert res.json()["data"]["member"]["id"] == "m-1"


def test_get_member_not_found_envelope(client):
    with patch("app.api.team.get_member") as mock_fn:
        mock_fn.return_value = {"ok": False, "error": "NOT_FOUND"}
        res = client.get("/api/team/members/nonexistent")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is False
    assert res.json()["error"]["code"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# POST /api/team/invitations
# ---------------------------------------------------------------------------


def test_invite_member_returns_envelope(client):
    with patch("app.api.team.invite_member") as mock_fn:
        mock_fn.return_value = {
            "ok": True,
            "invitation": {"id": "inv-1", "email": "new@test.com"},
        }
        res = client.post(
            "/api/team/invitations",
            json={"email": "new@test.com", "role": "viewer"},
        )
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is True
    assert res.json()["data"]["invitation"]["email"] == "new@test.com"


def test_invite_member_invalid_email_envelope(client):
    with patch("app.api.team.invite_member") as mock_fn:
        mock_fn.return_value = {"ok": False, "error": "INVALID_EMAIL"}
        res = client.post(
            "/api/team/invitations",
            json={"email": "bad", "role": "viewer"},
        )
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is False
    assert res.json()["error"]["code"] == "INVITE_FAILED"


def test_invite_member_validation_error(client):
    res = client.post(
        "/api/team/invitations",
        json={"email": "", "role": "viewer"},
    )
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/team/invitations
# ---------------------------------------------------------------------------


def test_list_invitations_returns_envelope(client):
    with patch("app.api.team.list_invitations") as mock_fn:
        mock_fn.return_value = {"ok": True, "invitations": []}
        res = client.get("/api/team/invitations")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is True
    assert "invitations" in res.json()["data"]


# ---------------------------------------------------------------------------
# PATCH /api/team/members/{member_id}/role
# ---------------------------------------------------------------------------


def test_update_role_returns_envelope(client):
    with patch("app.api.team.update_member_role") as mock_fn:
        mock_fn.return_value = {
            "ok": True,
            "member": {"id": "m-1", "role": "admin"},
        }
        res = client.patch(
            "/api/team/members/m-1/role",
            json={"role": "admin"},
        )
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is True
    assert res.json()["data"]["member"]["role"] == "admin"


def test_update_role_error_envelope(client):
    with patch("app.api.team.update_member_role") as mock_fn:
        mock_fn.return_value = {
            "ok": False,
            "error": "CANNOT_DOWNGRADE_LAST_OWNER",
        }
        res = client.patch(
            "/api/team/members/m-1/role",
            json={"role": "viewer"},
        )
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is False
    assert res.json()["error"]["code"] == "UPDATE_FAILED"


# ---------------------------------------------------------------------------
# POST /api/team/members/{member_id}/suspend
# ---------------------------------------------------------------------------


def test_suspend_member_returns_envelope(client):
    with patch("app.api.team.suspend_member") as mock_fn:
        mock_fn.return_value = {
            "ok": True,
            "member": {"id": "m-1", "status": "suspended"},
        }
        res = client.post("/api/team/members/m-1/suspend")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is True


def test_suspend_member_error_envelope(client):
    with patch("app.api.team.suspend_member") as mock_fn:
        mock_fn.return_value = {"ok": False, "error": "CANNOT_SUSPEND_SELF"}
        res = client.post("/api/team/members/m-1/suspend")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is False
    assert res.json()["error"]["code"] == "SUSPEND_FAILED"


# ---------------------------------------------------------------------------
# POST /api/team/members/{member_id}/reactivate
# ---------------------------------------------------------------------------


def test_reactivate_member_returns_envelope(client):
    with patch("app.api.team.reactivate_member") as mock_fn:
        mock_fn.return_value = {
            "ok": True,
            "member": {"id": "m-1", "status": "active"},
        }
        res = client.post("/api/team/members/m-1/reactivate")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is True


def test_reactivate_member_error_envelope(client):
    with patch("app.api.team.reactivate_member") as mock_fn:
        mock_fn.return_value = {"ok": False, "error": "MEMBER_NOT_FOUND"}
        res = client.post("/api/team/members/nonexistent/reactivate")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is False
    assert res.json()["error"]["code"] == "REACTIVATE_FAILED"


# ---------------------------------------------------------------------------
# DELETE /api/team/members/{member_id}
# ---------------------------------------------------------------------------


def test_remove_member_returns_envelope(client):
    with patch("app.api.team.remove_member") as mock_fn:
        mock_fn.return_value = {"ok": True}
        res = client.delete("/api/team/members/m-1")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is True


def test_remove_member_error_envelope(client):
    with patch("app.api.team.remove_member") as mock_fn:
        mock_fn.return_value = {
            "ok": False,
            "error": "CANNOT_REMOVE_LAST_OWNER",
        }
        res = client.delete("/api/team/members/m-1")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is False
    assert res.json()["error"]["code"] == "REMOVE_FAILED"


# ---------------------------------------------------------------------------
# GET /api/team/workspace-access?workspace_id=xxx
# ---------------------------------------------------------------------------


def test_list_workspace_access_returns_envelope(client):
    with patch("app.api.team.list_workspace_access") as mock_fn:
        mock_fn.return_value = {"ok": True, "access": []}
        res = client.get("/api/team/workspace-access", params={"workspace_id": "ws-1"})
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is True
    assert "access" in res.json()["data"]


def test_list_workspace_access_missing_param(client):
    res = client.get("/api/team/workspace-access")
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/team/workspace-access
# ---------------------------------------------------------------------------


def test_grant_workspace_access_returns_envelope(client):
    with patch("app.api.team.grant_workspace_access") as mock_fn:
        mock_fn.return_value = {
            "ok": True,
            "access": {
                "id": "a-1",
                "workspace_id": "ws-1",
                "member_id": "m-1",
                "access_level": "write",
            },
        }
        res = client.post(
            "/api/team/workspace-access",
            json={
                "workspace_id": "ws-1",
                "member_id": "m-1",
                "access_level": "write",
            },
        )
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is True
    assert res.json()["data"]["access"]["access_level"] == "write"


def test_grant_workspace_access_error_envelope(client):
    with patch("app.api.team.grant_workspace_access") as mock_fn:
        mock_fn.return_value = {"ok": False, "error": "INVALID_ACCESS_LEVEL"}
        res = client.post(
            "/api/team/workspace-access",
            json={
                "workspace_id": "ws-1",
                "member_id": "m-1",
                "access_level": "superuser",
            },
        )
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is False
    assert res.json()["error"]["code"] == "GRANT_FAILED"


# ---------------------------------------------------------------------------
# DELETE /api/team/workspace-access/{access_id}
# ---------------------------------------------------------------------------


def test_revoke_workspace_access_returns_envelope(client):
    with patch("app.api.team.revoke_workspace_access") as mock_fn:
        mock_fn.return_value = {"ok": True}
        res = client.delete("/api/team/workspace-access/a-1")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is True


def test_revoke_workspace_access_error_envelope(client):
    with patch("app.api.team.revoke_workspace_access") as mock_fn:
        mock_fn.return_value = {"ok": False, "error": "ACCESS_NOT_FOUND"}
        res = client.delete("/api/team/workspace-access/nonexistent")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is False
    assert res.json()["error"]["code"] == "REVOKE_FAILED"


# ---------------------------------------------------------------------------
# GET /api/team/agent-assignments
# ---------------------------------------------------------------------------


def test_list_agent_assignments_returns_envelope(client):
    with patch("app.api.team.list_agent_assignments") as mock_fn:
        mock_fn.return_value = {"ok": True, "assignments": []}
        res = client.get("/api/team/agent-assignments")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is True
    assert "assignments" in res.json()["data"]


# ---------------------------------------------------------------------------
# POST /api/team/agent-assignments
# ---------------------------------------------------------------------------


def test_assign_agent_returns_envelope(client):
    with patch("app.api.team.assign_agent") as mock_fn:
        mock_fn.return_value = {
            "ok": True,
            "assignment": {
                "id": "as-1",
                "agent_id": "agent-1",
                "assignment_role": "runner",
            },
        }
        res = client.post(
            "/api/team/agent-assignments",
            json={
                "workspace_id": "ws-1",
                "agent_id": "agent-1",
                "member_id": "m-1",
                "assignment_role": "runner",
            },
        )
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is True
    assert res.json()["data"]["assignment"]["agent_id"] == "agent-1"


def test_assign_agent_error_envelope(client):
    with patch("app.api.team.assign_agent") as mock_fn:
        mock_fn.return_value = {
            "ok": False,
            "error": "INVALID_ASSIGNMENT_ROLE",
        }
        res = client.post(
            "/api/team/agent-assignments",
            json={
                "workspace_id": "ws-1",
                "agent_id": "agent-1",
                "assignment_role": "captain",
            },
        )
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is False
    assert res.json()["error"]["code"] == "ASSIGN_FAILED"


# ---------------------------------------------------------------------------
# DELETE /api/team/agent-assignments/{assignment_id}
# ---------------------------------------------------------------------------


def test_unassign_agent_returns_envelope(client):
    with patch("app.api.team.unassign_agent") as mock_fn:
        mock_fn.return_value = {"ok": True}
        res = client.delete("/api/team/agent-assignments/as-1")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is True


def test_unassign_agent_error_envelope(client):
    with patch("app.api.team.unassign_agent") as mock_fn:
        mock_fn.return_value = {"ok": False, "error": "ASSIGNMENT_NOT_FOUND"}
        res = client.delete("/api/team/agent-assignments/nonexistent")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is False
    assert res.json()["error"]["code"] == "UNASSIGN_FAILED"


# ---------------------------------------------------------------------------
# GET /api/team/activity
# ---------------------------------------------------------------------------


def test_get_team_activity_returns_envelope(client):
    with patch("app.api.team.get_team_activity") as mock_fn:
        mock_fn.return_value = {"ok": True, "activities": []}
        res = client.get("/api/team/activity")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is True
    assert "activities" in res.json()["data"]


# ---------------------------------------------------------------------------
# GET /api/team/summary
# ---------------------------------------------------------------------------


def test_get_team_summary_returns_envelope(client):
    with patch("app.api.team.get_team_summary") as mock_fn:
        mock_fn.return_value = {
            "ok": True,
            "summary": {
                "total_members": 0,
                "active_members": 0,
                "pending_invitations": 0,
                "admins": 0,
                "operators": 0,
                "analysts": 0,
                "developers": 0,
                "viewers": 0,
                "is_last_owner": True,
            },
        }
        res = client.get("/api/team/summary")
    assert res.status_code == 200
    _assert_envelope(res.json())
    assert res.json()["ok"] is True
    assert "summary" in res.json()["data"]
