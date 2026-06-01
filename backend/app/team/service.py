from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.audit_service import AuditService
from app.audit.models import AuditLogCreate
from app.core.events import event_bus
from app.db.models import AuditLog
from app.db.session import SessionLocal
from app.team.models import (
    TeamAgentAssignment,
    TeamInvitation,
    TeamMember,
    TeamWorkspaceAccess,
)
from app.team.repositories import (
    TeamAgentAssignmentRepository,
    TeamInvitationRepository,
    TeamMemberRepository,
    TeamWorkspaceAccessRepository,
)

VALID_ROLES = {"owner", "admin", "operator", "analyst", "developer", "viewer"}
VALID_ACCESS_LEVELS = {"owner", "manage", "write", "read"}
VALID_ASSIGNMENT_ROLES = {"owner", "reviewer", "runner", "observer"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _session(db: Session | None) -> tuple[Session, bool]:
    if db is not None:
        return db, False
    return SessionLocal(), True


def _member_to_dict(m: TeamMember) -> dict[str, Any]:
    return {
        "id": m.id,
        "organization_id": m.organization_id,
        "workspace_id": m.workspace_id,
        "user_id": m.user_id,
        "email": m.email,
        "display_name": m.display_name,
        "role": m.role,
        "status": m.status,
        "avatar_url": m.avatar_url,
        "last_seen_at": m.last_seen_at.isoformat() if m.last_seen_at else None,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "updated_at": m.updated_at.isoformat() if m.updated_at else None,
    }


def _invitation_to_dict(inv: TeamInvitation) -> dict[str, Any]:
    return {
        "id": inv.id,
        "organization_id": inv.organization_id,
        "workspace_id": inv.workspace_id,
        "email": inv.email,
        "role": inv.role,
        "status": inv.status,
        "invited_by": inv.invited_by,
        "expires_at": inv.expires_at.isoformat() if inv.expires_at else None,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
    }


def _access_to_dict(a: TeamWorkspaceAccess) -> dict[str, Any]:
    return {
        "id": a.id,
        "organization_id": a.organization_id,
        "workspace_id": a.workspace_id,
        "member_id": a.member_id,
        "access_level": a.access_level,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def _assignment_to_dict(a: TeamAgentAssignment) -> dict[str, Any]:
    return {
        "id": a.id,
        "organization_id": a.organization_id,
        "workspace_id": a.workspace_id,
        "member_id": a.member_id,
        "agent_id": a.agent_id,
        "assignment_role": a.assignment_role,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def _log_audit(
    db: Session,
    actor: str,
    action: str,
    resource_type: str = "",
    resource_id: str = "",
    metadata: dict[str, Any] | None = None,
) -> None:
    try:
        svc = AuditService(db)
        svc.log(
            AuditLogCreate(
                actor_user_id=actor,
                actor_email=actor,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                metadata=metadata or {},
            )
        )
    except Exception:
        pass


# --- Member functions ---


def list_members(
    org_id: str, workspace_id: str | None = None, db: Session | None = None
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        repo = TeamMemberRepository(session)
        if workspace_id:
            members = repo.list_by_org_and_workspace(org_id, workspace_id)
        else:
            members = repo.list_by_org(org_id)
        return {"ok": True, "members": [_member_to_dict(m) for m in members]}
    finally:
        if own_session:
            session.close()


def get_member(
    org_id: str, member_id: str, db: Session | None = None
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        repo = TeamMemberRepository(session)
        member = repo.get_by_org(org_id, member_id)
        if not member:
            return {"ok": False, "error": "NOT_FOUND"}
        return {"ok": True, "member": _member_to_dict(member)}
    finally:
        if own_session:
            session.close()


def invite_member(
    org_id: str,
    workspace_id: str | None,
    email: str,
    role: str,
    invited_by: str,
    db: Session | None = None,
) -> dict[str, Any]:
    if "@" not in email:
        return {"ok": False, "error": "INVALID_EMAIL"}
    if role not in VALID_ROLES:
        return {"ok": False, "error": "INVALID_ROLE"}

    session, own_session = _session(db)
    try:
        member_repo = TeamMemberRepository(session)
        existing = member_repo.get_by_org_and_email(org_id, email)
        if existing:
            return {"ok": False, "error": "MEMBER_ALREADY_EXISTS"}

        inv_repo = TeamInvitationRepository(session)
        pending = inv_repo.get_by_org_and_email(org_id, email)
        if pending and pending.status == "pending":
            return {"ok": False, "error": "INVITATION_ALREADY_PENDING"}

        token_raw = str(uuid4())
        token_hash = hashlib.sha256(token_raw.encode()).hexdigest()
        expires_at = utc_now() + timedelta(days=7)

        invitation = inv_repo.create(
            organization_id=org_id,
            workspace_id=workspace_id,
            email=email,
            role=role,
            token_hash=token_hash,
            status="pending",
            invited_by=invited_by,
            expires_at=expires_at,
        )

        _log_audit(
            session,
            invited_by,
            "team.member.invited",
            "team_invitation",
            invitation.id,
            {"email": email, "role": role, "organization_id": org_id},
        )
        event_bus.emit(
            "team.member.invited",
            "team_service",
            f"Invited {email}",
            {
                "organization_id": org_id,
                "workspace_id": workspace_id,
                "email": email,
                "role": role,
                "invited_by": invited_by,
            },
        )
        return {"ok": True, "invitation": _invitation_to_dict(invitation)}
    finally:
        if own_session:
            session.close()


def resend_invitation(
    org_id: str, invitation_id: str, actor: str, db: Session | None = None
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        repo = TeamInvitationRepository(session)
        invitation = repo.get_by_org(org_id, invitation_id)
        if not invitation:
            return {"ok": False, "error": "INVITATION_NOT_FOUND"}
        if invitation.status != "pending":
            return {"ok": False, "error": "INVITATION_NOT_PENDING"}

        new_expires = utc_now() + timedelta(days=7)
        invitation.expires_at = new_expires
        session.commit()
        session.refresh(invitation)

        _log_audit(
            session,
            actor,
            "team.invitation.resend",
            "team_invitation",
            invitation.id,
            {"email": invitation.email},
        )
        return {"ok": True, "invitation": _invitation_to_dict(invitation)}
    finally:
        if own_session:
            session.close()


def revoke_invitation(
    org_id: str, invitation_id: str, actor: str, db: Session | None = None
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        repo = TeamInvitationRepository(session)
        invitation = repo.get_by_org(org_id, invitation_id)
        if not invitation:
            return {"ok": False, "error": "INVITATION_NOT_FOUND"}
        if invitation.status != "pending":
            return {"ok": False, "error": "INVITATION_NOT_PENDING"}

        invitation.status = "revoked"
        session.commit()
        session.refresh(invitation)

        _log_audit(
            session,
            actor,
            "team.invitation.revoked",
            "team_invitation",
            invitation.id,
            {"email": invitation.email},
        )
        return {"ok": True, "invitation": _invitation_to_dict(invitation)}
    finally:
        if own_session:
            session.close()


def update_member_role(
    org_id: str,
    member_id: str,
    role: str,
    actor: str,
    db: Session | None = None,
) -> dict[str, Any]:
    if role not in VALID_ROLES:
        return {"ok": False, "error": "INVALID_ROLE"}

    session, own_session = _session(db)
    try:
        repo = TeamMemberRepository(session)
        member = repo.get_by_org(org_id, member_id)
        if not member:
            return {"ok": False, "error": "MEMBER_NOT_FOUND"}

        if member.role == "owner" and role != "owner":
            owner_count = repo.count_by_org_and_role(org_id, "owner")
            if owner_count <= 1:
                return {"ok": False, "error": "CANNOT_DOWNGRADE_LAST_OWNER"}

        old_role = member.role
        member.role = role
        session.commit()
        session.refresh(member)

        _log_audit(
            session,
            actor,
            "team.member.role_updated",
            "team_member",
            member.id,
            {"old_role": old_role, "new_role": role},
        )
        return {"ok": True, "member": _member_to_dict(member)}
    finally:
        if own_session:
            session.close()


def suspend_member(
    org_id: str, member_id: str, actor: str, db: Session | None = None
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        repo = TeamMemberRepository(session)
        member = repo.get_by_org(org_id, member_id)
        if not member:
            return {"ok": False, "error": "MEMBER_NOT_FOUND"}
        if member.email == actor:
            return {"ok": False, "error": "CANNOT_SUSPEND_SELF"}

        member.status = "suspended"
        session.commit()
        session.refresh(member)

        _log_audit(
            session,
            actor,
            "team.member.suspended",
            "team_member",
            member.id,
            {"email": member.email},
        )
        return {"ok": True, "member": _member_to_dict(member)}
    finally:
        if own_session:
            session.close()


def reactivate_member(
    org_id: str, member_id: str, actor: str, db: Session | None = None
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        repo = TeamMemberRepository(session)
        member = repo.get_by_org(org_id, member_id)
        if not member:
            return {"ok": False, "error": "MEMBER_NOT_FOUND"}

        member.status = "active"
        session.commit()
        session.refresh(member)

        _log_audit(
            session,
            actor,
            "team.member.reactivated",
            "team_member",
            member.id,
            {"email": member.email},
        )
        return {"ok": True, "member": _member_to_dict(member)}
    finally:
        if own_session:
            session.close()


def remove_member(
    org_id: str, member_id: str, actor: str, db: Session | None = None
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        member_repo = TeamMemberRepository(session)
        member = member_repo.get_by_org(org_id, member_id)
        if not member:
            return {"ok": False, "error": "MEMBER_NOT_FOUND"}
        if member.email == actor:
            return {"ok": False, "error": "CANNOT_REMOVE_SELF"}
        if member.role == "owner":
            owner_count = member_repo.count_by_org_and_role(org_id, "owner")
            if owner_count <= 1:
                return {"ok": False, "error": "CANNOT_REMOVE_LAST_OWNER"}

        access_repo = TeamWorkspaceAccessRepository(session)
        for acc in access_repo.list_by_member(member_id):
            access_repo.delete(acc.id)

        assignment_repo = TeamAgentAssignmentRepository(session)
        q = select(TeamAgentAssignment).where(
            TeamAgentAssignment.member_id == member_id
        )
        for ass in list(session.execute(q).scalars().all()):
            assignment_repo.delete(ass.id)

        member_repo.delete(member_id)

        _log_audit(
            session,
            actor,
            "team.member.removed",
            "team_member",
            member_id,
            {"email": member.email},
        )
        return {"ok": True}
    finally:
        if own_session:
            session.close()


# --- Invitation functions ---


def list_invitations(
    org_id: str, workspace_id: str | None = None, db: Session | None = None
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        repo = TeamInvitationRepository(session)
        if workspace_id:
            invitations = repo.list_by_org_and_workspace(org_id, workspace_id)
        else:
            invitations = repo.list_by_org(org_id)
        return {
            "ok": True,
            "invitations": [_invitation_to_dict(inv) for inv in invitations],
        }
    finally:
        if own_session:
            session.close()


# --- Workspace access functions ---


def list_workspace_access(
    org_id: str, workspace_id: str, db: Session | None = None
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        repo = TeamWorkspaceAccessRepository(session)
        access_list = repo.list_by_org_and_workspace(org_id, workspace_id)
        return {
            "ok": True,
            "access": [_access_to_dict(a) for a in access_list],
        }
    finally:
        if own_session:
            session.close()


def grant_workspace_access(
    org_id: str,
    workspace_id: str,
    member_id: str,
    access_level: str,
    actor: str,
    db: Session | None = None,
) -> dict[str, Any]:
    if access_level not in VALID_ACCESS_LEVELS:
        return {"ok": False, "error": "INVALID_ACCESS_LEVEL"}

    session, own_session = _session(db)
    try:
        repo = TeamWorkspaceAccessRepository(session)
        existing_list = repo.list_by_org_and_workspace(org_id, workspace_id)
        existing = next((a for a in existing_list if a.member_id == member_id), None)
        if existing:
            existing.access_level = access_level
            session.commit()
            session.refresh(existing)
            row = existing
        else:
            row = repo.create(
                organization_id=org_id,
                workspace_id=workspace_id,
                member_id=member_id,
                access_level=access_level,
            )

        _log_audit(
            session,
            actor,
            "team.workspace.access_granted",
            "team_workspace_access",
            row.id,
            {
                "workspace_id": workspace_id,
                "member_id": member_id,
                "access_level": access_level,
            },
        )
        return {"ok": True, "access": _access_to_dict(row)}
    finally:
        if own_session:
            session.close()


def revoke_workspace_access(
    org_id: str, access_id: str, actor: str, db: Session | None = None
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        repo = TeamWorkspaceAccessRepository(session)
        access = repo.get_by_id(access_id)
        if not access:
            return {"ok": False, "error": "ACCESS_NOT_FOUND"}
        if access.organization_id != org_id:
            return {"ok": False, "error": "ACCESS_NOT_FOUND"}

        repo.delete(access_id)

        _log_audit(
            session,
            actor,
            "team.workspace.access_revoked",
            "team_workspace_access",
            access_id,
            {"workspace_id": access.workspace_id, "member_id": access.member_id},
        )
        return {"ok": True}
    finally:
        if own_session:
            session.close()


# --- Agent assignment functions ---


def list_agent_assignments(
    org_id: str, workspace_id: str | None = None, db: Session | None = None
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        repo = TeamAgentAssignmentRepository(session)
        if workspace_id:
            assignments = repo.list_by_org_and_workspace(org_id, workspace_id)
        else:
            assignments = repo.list_by_org(org_id)
        return {
            "ok": True,
            "assignments": [_assignment_to_dict(a) for a in assignments],
        }
    finally:
        if own_session:
            session.close()


def assign_agent(
    org_id: str,
    workspace_id: str,
    agent_id: str,
    member_id: str | None,
    assignment_role: str,
    actor: str,
    db: Session | None = None,
) -> dict[str, Any]:
    if assignment_role not in VALID_ASSIGNMENT_ROLES:
        return {"ok": False, "error": "INVALID_ASSIGNMENT_ROLE"}

    session, own_session = _session(db)
    try:
        repo = TeamAgentAssignmentRepository(session)
        row = repo.create(
            organization_id=org_id,
            workspace_id=workspace_id,
            member_id=member_id,
            agent_id=agent_id,
            assignment_role=assignment_role,
        )

        _log_audit(
            session,
            actor,
            "team.agent.assigned",
            "team_agent_assignment",
            row.id,
            {
                "workspace_id": workspace_id,
                "agent_id": agent_id,
                "member_id": member_id or "",
                "assignment_role": assignment_role,
            },
        )
        return {"ok": True, "assignment": _assignment_to_dict(row)}
    finally:
        if own_session:
            session.close()


def unassign_agent(
    org_id: str, assignment_id: str, actor: str, db: Session | None = None
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        repo = TeamAgentAssignmentRepository(session)
        assignment = repo.get_by_id(assignment_id)
        if not assignment:
            return {"ok": False, "error": "ASSIGNMENT_NOT_FOUND"}
        if assignment.organization_id != org_id:
            return {"ok": False, "error": "ASSIGNMENT_NOT_FOUND"}

        repo.delete(assignment_id)

        _log_audit(
            session,
            actor,
            "team.agent.unassigned",
            "team_agent_assignment",
            assignment_id,
            {
                "agent_id": assignment.agent_id,
                "workspace_id": assignment.workspace_id,
            },
        )
        return {"ok": True}
    finally:
        if own_session:
            session.close()


# --- Activity and summary ---


def get_team_activity(
    org_id: str,
    workspace_id: str | None = None,
    limit: int = 20,
    db: Session | None = None,
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        q = (
            select(AuditLog)
            .where(AuditLog.action.ilike("team.%"))
            .order_by(AuditLog.created_at.desc())
            .limit(max(1, min(limit, 100)))
        )
        rows = list(session.execute(q).scalars().all())
        activities = []
        for r in rows:
            activities.append(
                {
                    "id": r.id,
                    "action": r.action,
                    "actor": r.actor_email or "",
                    "details": str(r.metadata_json) if r.metadata_json else "",
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
            )
        return {"ok": True, "activities": activities}
    finally:
        if own_session:
            session.close()


def get_team_summary(org_id: str, db: Session | None = None) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        repo = TeamMemberRepository(session)
        total = repo.count_by_org(org_id)
        active = repo.count_by_org_and_status(org_id, "active")

        roles = {
            "admins": repo.count_by_org_and_role(org_id, "admin"),
            "operators": repo.count_by_org_and_role(org_id, "operator"),
            "analysts": repo.count_by_org_and_role(org_id, "analyst"),
            "developers": repo.count_by_org_and_role(org_id, "developer"),
            "viewers": repo.count_by_org_and_role(org_id, "viewer"),
        }

        inv_repo = TeamInvitationRepository(session)
        invitations = inv_repo.list_by_org(org_id)
        pending_invitations = sum(1 for inv in invitations if inv.status == "pending")

        owner_count = repo.count_by_org_and_role(org_id, "owner")
        is_last_owner = owner_count <= 1

        return {
            "ok": True,
            "summary": {
                "total_members": total,
                "active_members": active,
                "pending_invitations": pending_invitations,
                **roles,
                "is_last_owner": is_last_owner,
            },
        }
    finally:
        if own_session:
            session.close()
