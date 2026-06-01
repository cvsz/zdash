from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import AuditLog
from app.team.repositories import (
    TeamAgentAssignmentRepository,
    TeamInvitationRepository,
    TeamMemberRepository,
    TeamWorkspaceAccessRepository,
)
from app.team.service import (
    assign_agent,
    get_member,
    get_team_activity,
    get_team_summary,
    grant_workspace_access,
    invite_member,
    list_agent_assignments,
    list_invitations,
    list_members,
    list_workspace_access,
    reactivate_member,
    remove_member,
    revoke_workspace_access,
    suspend_member,
    unassign_agent,
    update_member_role,
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite://", echo=False)
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Member list / get
# ---------------------------------------------------------------------------


def test_list_members_returns_empty(db_session):
    result = list_members("org-1", db=db_session)
    assert result["ok"] is True
    assert result["members"] == []


def test_list_members_with_data(db_session):
    repo = TeamMemberRepository(db_session)
    repo.create(
        organization_id="org-1",
        email="alice@test.com",
        role="admin",
        display_name="Alice",
    )

    result = list_members("org-1", db=db_session)
    assert result["ok"] is True
    assert len(result["members"]) == 1
    assert result["members"][0]["email"] == "alice@test.com"


def test_list_members_filters_by_workspace(db_session):
    repo = TeamMemberRepository(db_session)
    repo.create(
        organization_id="org-1",
        workspace_id="ws-1",
        email="a@test.com",
        role="viewer",
    )
    repo.create(
        organization_id="org-1",
        workspace_id="ws-2",
        email="b@test.com",
        role="viewer",
    )

    r1 = list_members("org-1", workspace_id="ws-1", db=db_session)
    assert len(r1["members"]) == 1
    assert r1["members"][0]["email"] == "a@test.com"

    r2 = list_members("org-1", workspace_id="ws-2", db=db_session)
    assert len(r2["members"]) == 1
    assert r2["members"][0]["email"] == "b@test.com"


def test_get_member_found(db_session):
    repo = TeamMemberRepository(db_session)
    m = repo.create(organization_id="org-1", email="bob@test.com", role="operator")

    result = get_member("org-1", m.id, db=db_session)
    assert result["ok"] is True
    assert result["member"]["email"] == "bob@test.com"


def test_get_member_not_found(db_session):
    result = get_member("org-1", "nonexistent", db=db_session)
    assert result["ok"] is False
    assert result["error"] == "NOT_FOUND"


def test_get_member_wrong_org(db_session):
    repo = TeamMemberRepository(db_session)
    m = repo.create(organization_id="org-1", email="bob@test.com", role="operator")

    result = get_member("org-2", m.id, db=db_session)
    assert result["ok"] is False
    assert result["error"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# Invite member
# ---------------------------------------------------------------------------


def test_invite_member_creates_invitation(db_session):
    result = invite_member(
        "org-1", "ws-1", "new@test.com", "viewer", "admin@test.com", db=db_session
    )
    assert result["ok"] is True
    assert "invitation" in result
    assert result["invitation"]["email"] == "new@test.com"
    assert result["invitation"]["status"] == "pending"
    assert result["invitation"]["invited_by"] == "admin@test.com"


def test_invite_member_invalid_email(db_session):
    result = invite_member(
        "org-1", None, "invalid-email", "viewer", "admin@test.com", db=db_session
    )
    assert result["ok"] is False
    assert result["error"] == "INVALID_EMAIL"


def test_invite_member_invalid_role(db_session):
    result = invite_member(
        "org-1", None, "new@test.com", "superadmin", "admin@test.com", db=db_session
    )
    assert result["ok"] is False
    assert result["error"] == "INVALID_ROLE"


def test_invite_member_already_exists(db_session):
    repo = TeamMemberRepository(db_session)
    repo.create(organization_id="org-1", email="exists@test.com", role="viewer")

    result = invite_member(
        "org-1", None, "exists@test.com", "viewer", "admin@test.com", db=db_session
    )
    assert result["ok"] is False
    assert result["error"] == "MEMBER_ALREADY_EXISTS"


def test_invite_member_duplicate_pending(db_session):
    inv_repo = TeamInvitationRepository(db_session)
    inv_repo.create(
        organization_id="org-1",
        email="dup@test.com",
        role="viewer",
        token_hash="abc",
        status="pending",
        invited_by="admin@test.com",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    result = invite_member(
        "org-1", None, "dup@test.com", "viewer", "admin@test.com", db=db_session
    )
    assert result["ok"] is False
    assert result["error"] == "INVITATION_ALREADY_PENDING"


# ---------------------------------------------------------------------------
# Update member role
# ---------------------------------------------------------------------------


def test_update_member_role_success(db_session):
    repo = TeamMemberRepository(db_session)
    m = repo.create(organization_id="org-1", email="u@test.com", role="viewer")

    result = update_member_role("org-1", m.id, "admin", "actor", db=db_session)
    assert result["ok"] is True
    assert result["member"]["role"] == "admin"


def test_update_member_role_invalid_role(db_session):
    repo = TeamMemberRepository(db_session)
    m = repo.create(organization_id="org-1", email="u@test.com", role="viewer")

    result = update_member_role("org-1", m.id, "god", "actor", db=db_session)
    assert result["ok"] is False
    assert result["error"] == "INVALID_ROLE"


def test_update_member_role_not_found(db_session):
    result = update_member_role("org-1", "nonexistent", "admin", "actor", db=db_session)
    assert result["ok"] is False
    assert result["error"] == "MEMBER_NOT_FOUND"


def test_cannot_downgrade_last_owner(db_session):
    repo = TeamMemberRepository(db_session)
    owner = repo.create(organization_id="org-1", email="owner@test.com", role="owner")

    result = update_member_role("org-1", owner.id, "viewer", "actor", db=db_session)
    assert result["ok"] is False
    assert result["error"] == "CANNOT_DOWNGRADE_LAST_OWNER"


def test_can_downgrade_when_multiple_owners(db_session):
    repo = TeamMemberRepository(db_session)
    o1 = repo.create(organization_id="org-1", email="owner1@test.com", role="owner")
    repo.create(organization_id="org-1", email="owner2@test.com", role="owner")

    result = update_member_role("org-1", o1.id, "viewer", "actor", db=db_session)
    assert result["ok"] is True
    assert result["member"]["role"] == "viewer"


# ---------------------------------------------------------------------------
# Suspend / reactivate
# ---------------------------------------------------------------------------


def test_suspend_member_success(db_session):
    repo = TeamMemberRepository(db_session)
    m = repo.create(organization_id="org-1", email="sus@test.com", role="viewer")

    result = suspend_member("org-1", m.id, "actor@test.com", db=db_session)
    assert result["ok"] is True
    assert result["member"]["status"] == "suspended"


def test_suspend_member_not_found(db_session):
    result = suspend_member("org-1", "nonexistent", "actor", db=db_session)
    assert result["ok"] is False
    assert result["error"] == "MEMBER_NOT_FOUND"


def test_suspend_self_not_allowed(db_session):
    repo = TeamMemberRepository(db_session)
    m = repo.create(organization_id="org-1", email="self@test.com", role="viewer")

    result = suspend_member("org-1", m.id, "self@test.com", db=db_session)
    assert result["ok"] is False
    assert result["error"] == "CANNOT_SUSPEND_SELF"


def test_reactivate_member_success(db_session):
    repo = TeamMemberRepository(db_session)
    m = repo.create(
        organization_id="org-1", email="re@test.com", role="viewer", status="suspended"
    )

    result = reactivate_member("org-1", m.id, "actor@test.com", db=db_session)
    assert result["ok"] is True
    assert result["member"]["status"] == "active"


def test_reactivate_member_not_found(db_session):
    result = reactivate_member("org-1", "nonexistent", "actor", db=db_session)
    assert result["ok"] is False
    assert result["error"] == "MEMBER_NOT_FOUND"


# ---------------------------------------------------------------------------
# Remove member
# ---------------------------------------------------------------------------


def test_remove_member_success(db_session):
    repo = TeamMemberRepository(db_session)
    m = repo.create(organization_id="org-1", email="rm@test.com", role="viewer")

    result = remove_member("org-1", m.id, "actor@test.com", db=db_session)
    assert result["ok"] is True

    remaining = repo.list_by_org("org-1")
    assert len(remaining) == 0


def test_remove_member_not_found(db_session):
    result = remove_member("org-1", "nonexistent", "actor", db=db_session)
    assert result["ok"] is False
    assert result["error"] == "MEMBER_NOT_FOUND"


def test_remove_member_cannot_remove_self(db_session):
    repo = TeamMemberRepository(db_session)
    m = repo.create(organization_id="org-1", email="self@test.com", role="viewer")

    result = remove_member("org-1", m.id, "self@test.com", db=db_session)
    assert result["ok"] is False
    assert result["error"] == "CANNOT_REMOVE_SELF"


def test_remove_member_cannot_remove_last_owner(db_session):
    repo = TeamMemberRepository(db_session)
    m = repo.create(organization_id="org-1", email="owner@test.com", role="owner")

    result = remove_member("org-1", m.id, "admin@test.com", db=db_session)
    assert result["ok"] is False
    assert result["error"] == "CANNOT_REMOVE_LAST_OWNER"


def test_remove_member_removes_access_and_assignments(db_session):
    member_repo = TeamMemberRepository(db_session)
    m = member_repo.create(
        organization_id="org-1", email="multi@test.com", role="viewer"
    )

    access_repo = TeamWorkspaceAccessRepository(db_session)
    access_repo.create(
        organization_id="org-1",
        workspace_id="ws-1",
        member_id=m.id,
        access_level="write",
    )

    agent_repo = TeamAgentAssignmentRepository(db_session)
    agent_repo.create(
        organization_id="org-1",
        workspace_id="ws-1",
        member_id=m.id,
        agent_id="agent-1",
        assignment_role="observer",
    )

    result = remove_member("org-1", m.id, "admin@test.com", db=db_session)
    assert result["ok"] is True

    assert access_repo.list_by_member(m.id) == []
    assert agent_repo.list_by_org("org-1") == []


# ---------------------------------------------------------------------------
# List invitations
# ---------------------------------------------------------------------------


def test_list_invitations_empty(db_session):
    result = list_invitations("org-1", db=db_session)
    assert result["ok"] is True
    assert result["invitations"] == []


def test_list_invitations_with_data(db_session):
    inv_repo = TeamInvitationRepository(db_session)
    inv_repo.create(
        organization_id="org-1",
        email="inv@test.com",
        role="admin",
        token_hash="abc",
        status="pending",
        invited_by="admin@test.com",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    result = list_invitations("org-1", db=db_session)
    assert len(result["invitations"]) == 1
    assert result["invitations"][0]["email"] == "inv@test.com"


# ---------------------------------------------------------------------------
# Workspace access
# ---------------------------------------------------------------------------


def test_list_workspace_access_empty(db_session):
    result = list_workspace_access("org-1", "ws-1", db=db_session)
    assert result["ok"] is True
    assert result["access"] == []


def test_list_workspace_access_with_data(db_session):
    access_repo = TeamWorkspaceAccessRepository(db_session)
    access_repo.create(
        organization_id="org-1",
        workspace_id="ws-1",
        member_id="m-1",
        access_level="write",
    )

    result = list_workspace_access("org-1", "ws-1", db=db_session)
    assert len(result["access"]) == 1
    assert result["access"][0]["access_level"] == "write"


def test_grant_workspace_access_creates_new(db_session):
    result = grant_workspace_access(
        "org-1", "ws-1", "m-1", "write", "actor@test.com", db=db_session
    )
    assert result["ok"] is True
    assert result["access"]["member_id"] == "m-1"
    assert result["access"]["access_level"] == "write"


def test_grant_workspace_access_updates_existing(db_session):
    access_repo = TeamWorkspaceAccessRepository(db_session)
    a = access_repo.create(
        organization_id="org-1",
        workspace_id="ws-1",
        member_id="m-1",
        access_level="read",
    )

    result = grant_workspace_access(
        "org-1", "ws-1", "m-1", "manage", "actor@test.com", db=db_session
    )
    assert result["ok"] is True
    assert result["access"]["id"] == a.id
    assert result["access"]["access_level"] == "manage"


def test_grant_workspace_access_invalid_level(db_session):
    result = grant_workspace_access(
        "org-1", "ws-1", "m-1", "superuser", "actor", db=db_session
    )
    assert result["ok"] is False
    assert result["error"] == "INVALID_ACCESS_LEVEL"


def test_revoke_workspace_access_success(db_session):
    access_repo = TeamWorkspaceAccessRepository(db_session)
    a = access_repo.create(
        organization_id="org-1",
        workspace_id="ws-1",
        member_id="m-1",
        access_level="read",
    )

    result = revoke_workspace_access("org-1", a.id, "actor@test.com", db=db_session)
    assert result["ok"] is True

    assert access_repo.get_by_id(a.id) is None


def test_revoke_workspace_access_not_found(db_session):
    result = revoke_workspace_access("org-1", "nonexistent", "actor", db=db_session)
    assert result["ok"] is False
    assert result["error"] == "ACCESS_NOT_FOUND"


def test_revoke_workspace_access_wrong_org(db_session):
    access_repo = TeamWorkspaceAccessRepository(db_session)
    a = access_repo.create(
        organization_id="org-1",
        workspace_id="ws-1",
        member_id="m-1",
        access_level="read",
    )

    result = revoke_workspace_access("org-2", a.id, "actor", db=db_session)
    assert result["ok"] is False
    assert result["error"] == "ACCESS_NOT_FOUND"


# ---------------------------------------------------------------------------
# Agent assignments
# ---------------------------------------------------------------------------


def test_list_agent_assignments_empty(db_session):
    result = list_agent_assignments("org-1", db=db_session)
    assert result["ok"] is True
    assert result["assignments"] == []


def test_list_agent_assignments_with_data(db_session):
    agent_repo = TeamAgentAssignmentRepository(db_session)
    agent_repo.create(
        organization_id="org-1",
        workspace_id="ws-1",
        member_id="m-1",
        agent_id="agent-1",
        assignment_role="reviewer",
    )

    result = list_agent_assignments("org-1", db=db_session)
    assert len(result["assignments"]) == 1
    assert result["assignments"][0]["assignment_role"] == "reviewer"


def test_assign_agent_success(db_session):
    result = assign_agent(
        "org-1", "ws-1", "agent-1", "m-1", "runner", "actor@test.com", db=db_session
    )
    assert result["ok"] is True
    assert result["assignment"]["agent_id"] == "agent-1"
    assert result["assignment"]["assignment_role"] == "runner"


def test_assign_agent_invalid_role(db_session):
    result = assign_agent(
        "org-1", "ws-1", "agent-1", "m-1", "captain", "actor", db=db_session
    )
    assert result["ok"] is False
    assert result["error"] == "INVALID_ASSIGNMENT_ROLE"


def test_assign_agent_no_member(db_session):
    result = assign_agent(
        "org-1", "ws-1", "agent-1", None, "observer", "actor@test.com", db=db_session
    )
    assert result["ok"] is True
    assert result["assignment"]["member_id"] is None


def test_unassign_agent_success(db_session):
    agent_repo = TeamAgentAssignmentRepository(db_session)
    a = agent_repo.create(
        organization_id="org-1",
        workspace_id="ws-1",
        member_id="m-1",
        agent_id="agent-1",
        assignment_role="observer",
    )

    result = unassign_agent("org-1", a.id, "actor@test.com", db=db_session)
    assert result["ok"] is True

    assert agent_repo.get_by_id(a.id) is None


def test_unassign_agent_not_found(db_session):
    result = unassign_agent("org-1", "nonexistent", "actor", db=db_session)
    assert result["ok"] is False
    assert result["error"] == "ASSIGNMENT_NOT_FOUND"


def test_unassign_agent_wrong_org(db_session):
    agent_repo = TeamAgentAssignmentRepository(db_session)
    a = agent_repo.create(
        organization_id="org-1",
        workspace_id="ws-1",
        member_id="m-1",
        agent_id="agent-1",
        assignment_role="observer",
    )

    result = unassign_agent("org-2", a.id, "actor", db=db_session)
    assert result["ok"] is False
    assert result["error"] == "ASSIGNMENT_NOT_FOUND"


# ---------------------------------------------------------------------------
# Team activity
# ---------------------------------------------------------------------------


def test_get_team_activity_empty(db_session):
    result = get_team_activity("org-1", db=db_session)
    assert result["ok"] is True
    assert result["activities"] == []


def test_get_team_activity_returns_audit_logs(db_session):
    now = datetime.now(timezone.utc)
    log = AuditLog(
        id="log-1",
        actor_email="admin@test.com",
        action="team.member.invited",
        resource_type="team_invitation",
        resource_id="inv-1",
        metadata_json={"email": "new@test.com"},
        created_at=now,
    )
    db_session.add(log)
    db_session.commit()

    result = get_team_activity("org-1", db=db_session)
    assert result["ok"] is True
    assert len(result["activities"]) == 1
    entry = result["activities"][0]
    assert entry["action"] == "team.member.invited"
    assert entry["actor"] == "admin@test.com"


def test_get_team_activity_respects_limit(db_session):
    now = datetime.now(timezone.utc)
    for i in range(5):
        db_session.add(
            AuditLog(
                id=f"log-{i}",
                actor_email="admin@test.com",
                action="team.member.invited",
                resource_type="team_invitation",
                resource_id=f"inv-{i}",
                metadata_json={},
                created_at=now,
            )
        )
    db_session.commit()

    result = get_team_activity("org-1", limit=3, db=db_session)
    assert len(result["activities"]) == 3


# ---------------------------------------------------------------------------
# Team summary
# ---------------------------------------------------------------------------


def test_get_team_summary_empty(db_session):
    result = get_team_summary("org-1", db=db_session)
    assert result["ok"] is True
    s = result["summary"]
    assert s["total_members"] == 0
    assert s["active_members"] == 0
    assert s["pending_invitations"] == 0
    assert s["is_last_owner"] is True


def test_get_team_summary_with_members(db_session):
    repo = TeamMemberRepository(db_session)
    repo.create(organization_id="org-1", email="owner@test.com", role="owner")
    repo.create(organization_id="org-1", email="admin@test.com", role="admin")
    repo.create(organization_id="org-1", email="op@test.com", role="operator")
    repo.create(organization_id="org-1", email="analyst@test.com", role="analyst")
    repo.create(organization_id="org-1", email="dev@test.com", role="developer")
    repo.create(organization_id="org-1", email="viewer@test.com", role="viewer")

    result = get_team_summary("org-1", db=db_session)
    s = result["summary"]
    assert s["total_members"] == 6
    assert s["active_members"] == 6
    assert s["admins"] == 1
    assert s["operators"] == 1
    assert s["analysts"] == 1
    assert s["developers"] == 1
    assert s["viewers"] == 1
    assert s["is_last_owner"] is True


def test_get_team_summary_pending_invitations(db_session):
    inv_repo = TeamInvitationRepository(db_session)
    inv_repo.create(
        organization_id="org-1",
        email="inv@test.com",
        role="viewer",
        token_hash="abc",
        status="pending",
        invited_by="admin@test.com",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    result = get_team_summary("org-1", db=db_session)
    assert result["summary"]["pending_invitations"] == 1


def test_get_team_summary_is_last_owner_false(db_session):
    repo = TeamMemberRepository(db_session)
    repo.create(organization_id="org-1", email="o1@test.com", role="owner")
    repo.create(organization_id="org-1", email="o2@test.com", role="owner")

    result = get_team_summary("org-1", db=db_session)
    assert result["summary"]["is_last_owner"] is False
