from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import require_permissions
from app.auth.models import AuthSession
from app.auth.rbac import Permission
from app.core.responses import error_response, success_response
from app.db.session import get_db_session
from app.team.schemas import (
    AssignAgentRequest,
    GrantAccessRequest,
    InviteMemberRequest,
    UpdateRoleRequest,
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
    resend_invitation,
    revoke_invitation,
    revoke_workspace_access,
    suspend_member,
    unassign_agent,
    update_member_role,
)

router = APIRouter(prefix="/api/team", tags=["team"])


def _get_org(current_user: AuthSession) -> str:
    return getattr(current_user, "organization_id", None) or current_user.username


@router.get("/members")
def api_list_members(
    workspace_id: str | None = Query(default=None),
    current_user: AuthSession = Depends(require_permissions([Permission.team_read])),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        result = list_members(org_id, workspace_id, db)
        return success_response({"members": result.get("members", [])})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.get("/members/{member_id}")
def api_get_member(
    member_id: str,
    current_user: AuthSession = Depends(require_permissions([Permission.team_read])),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        result = get_member(org_id, member_id, db)
        if not result.get("ok"):
            return error_response("NOT_FOUND", result.get("error", ""))
        return success_response({"member": result["member"]})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.post("/invitations")
def api_invite_member(
    body: InviteMemberRequest,
    current_user: AuthSession = Depends(require_permissions([Permission.team_invite])),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        actor = current_user.username
        result = invite_member(
            org_id, body.workspace_id, body.email, body.role, actor, db
        )
        if not result.get("ok"):
            return error_response("INVITE_FAILED", result.get("error", ""))
        return success_response({"invitation": result["invitation"]})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.get("/invitations")
def api_list_invitations(
    workspace_id: str | None = Query(default=None),
    current_user: AuthSession = Depends(require_permissions([Permission.team_read])),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        result = list_invitations(org_id, workspace_id, db)
        return success_response({"invitations": result.get("invitations", [])})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.post("/invitations/{invitation_id}/resend")
def api_resend_invitation(
    invitation_id: str,
    current_user: AuthSession = Depends(require_permissions([Permission.team_invite])),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        actor = current_user.username
        result = resend_invitation(org_id, invitation_id, actor, db)
        if not result.get("ok"):
            return error_response("RESEND_FAILED", result.get("error", ""))
        return success_response({"invitation": result["invitation"]})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.post("/invitations/{invitation_id}/revoke")
def api_revoke_invitation(
    invitation_id: str,
    current_user: AuthSession = Depends(require_permissions([Permission.team_invite])),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        actor = current_user.username
        result = revoke_invitation(org_id, invitation_id, actor, db)
        if not result.get("ok"):
            return error_response("REVOKE_FAILED", result.get("error", ""))
        return success_response({"invitation": result["invitation"]})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.patch("/members/{member_id}/role")
def api_update_member_role(
    member_id: str,
    body: UpdateRoleRequest,
    current_user: AuthSession = Depends(require_permissions([Permission.team_manage])),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        actor = current_user.username
        result = update_member_role(org_id, member_id, body.role, actor, db)
        if not result.get("ok"):
            return error_response("UPDATE_FAILED", result.get("error", ""))
        return success_response({"member": result["member"]})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.post("/members/{member_id}/suspend")
def api_suspend_member(
    member_id: str,
    current_user: AuthSession = Depends(require_permissions([Permission.team_manage])),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        actor = current_user.username
        result = suspend_member(org_id, member_id, actor, db)
        if not result.get("ok"):
            return error_response("SUSPEND_FAILED", result.get("error", ""))
        return success_response({"member": result["member"]})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.post("/members/{member_id}/reactivate")
def api_reactivate_member(
    member_id: str,
    current_user: AuthSession = Depends(require_permissions([Permission.team_manage])),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        actor = current_user.username
        result = reactivate_member(org_id, member_id, actor, db)
        if not result.get("ok"):
            return error_response("REACTIVATE_FAILED", result.get("error", ""))
        return success_response({"member": result["member"]})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.delete("/members/{member_id}")
def api_remove_member(
    member_id: str,
    current_user: AuthSession = Depends(require_permissions([Permission.team_remove])),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        actor = current_user.username
        result = remove_member(org_id, member_id, actor, db)
        if not result.get("ok"):
            return error_response("REMOVE_FAILED", result.get("error", ""))
        return success_response({})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.get("/workspace-access")
def api_list_workspace_access(
    workspace_id: str = Query(...),
    current_user: AuthSession = Depends(require_permissions([Permission.team_manage])),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        result = list_workspace_access(org_id, workspace_id, db)
        return success_response({"access": result.get("access", [])})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.post("/workspace-access")
def api_grant_workspace_access(
    body: GrantAccessRequest,
    current_user: AuthSession = Depends(require_permissions([Permission.team_manage])),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        actor = current_user.username
        result = grant_workspace_access(
            org_id, body.workspace_id, body.member_id, body.access_level, actor, db
        )
        if not result.get("ok"):
            return error_response("GRANT_FAILED", result.get("error", ""))
        return success_response({"access": result["access"]})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.delete("/workspace-access/{access_id}")
def api_revoke_workspace_access(
    access_id: str,
    current_user: AuthSession = Depends(require_permissions([Permission.team_manage])),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        actor = current_user.username
        result = revoke_workspace_access(org_id, access_id, actor, db)
        if not result.get("ok"):
            return error_response("REVOKE_FAILED", result.get("error", ""))
        return success_response({})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.get("/agent-assignments")
def api_list_agent_assignments(
    workspace_id: str | None = Query(default=None),
    current_user: AuthSession = Depends(require_permissions([Permission.team_read])),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        result = list_agent_assignments(org_id, workspace_id, db)
        return success_response({"assignments": result.get("assignments", [])})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.post("/agent-assignments")
def api_assign_agent(
    body: AssignAgentRequest,
    current_user: AuthSession = Depends(
        require_permissions([Permission.team_assign_agents])
    ),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        actor = current_user.username
        result = assign_agent(
            org_id,
            body.workspace_id,
            body.agent_id,
            body.member_id,
            body.assignment_role,
            actor,
            db,
        )
        if not result.get("ok"):
            return error_response("ASSIGN_FAILED", result.get("error", ""))
        return success_response({"assignment": result["assignment"]})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.delete("/agent-assignments/{assignment_id}")
def api_unassign_agent(
    assignment_id: str,
    current_user: AuthSession = Depends(
        require_permissions([Permission.team_assign_agents])
    ),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        actor = current_user.username
        result = unassign_agent(org_id, assignment_id, actor, db)
        if not result.get("ok"):
            return error_response("UNASSIGN_FAILED", result.get("error", ""))
        return success_response({})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.get("/activity")
def api_get_team_activity(
    workspace_id: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: AuthSession = Depends(require_permissions([Permission.team_read])),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        result = get_team_activity(org_id, workspace_id, limit, db)
        return success_response({"activities": result.get("activities", [])})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))


@router.get("/summary")
def api_get_team_summary(
    current_user: AuthSession = Depends(require_permissions([Permission.team_read])),
    db=Depends(get_db_session),
):
    try:
        org_id = _get_org(current_user)
        result = get_team_summary(org_id, db)
        if not result.get("ok"):
            return error_response("SUMMARY_ERROR", result.get("error", ""))
        return success_response({"summary": result["summary"]})
    except Exception as e:
        return error_response("TEAM_ERROR", str(e))
