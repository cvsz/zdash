from datetime import datetime

from pydantic import BaseModel, Field


class TeamMemberResponse(BaseModel):
    id: str
    organization_id: str
    workspace_id: str | None = None
    user_id: str | None = None
    email: str
    display_name: str = ""
    role: str
    status: str
    avatar_url: str | None = None
    last_seen_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TeamInvitationResponse(BaseModel):
    id: str
    organization_id: str
    workspace_id: str | None = None
    email: str
    role: str
    status: str
    invited_by: str = ""
    expires_at: datetime | None = None
    created_at: datetime | None = None


class TeamWorkspaceAccessResponse(BaseModel):
    id: str
    organization_id: str
    workspace_id: str
    member_id: str
    access_level: str
    created_at: datetime | None = None


class TeamAgentAssignmentResponse(BaseModel):
    id: str
    organization_id: str
    workspace_id: str
    member_id: str | None = None
    agent_id: str
    assignment_role: str
    created_at: datetime | None = None


class TeamActivityResponse(BaseModel):
    id: str
    action: str
    actor: str
    details: str
    created_at: datetime | None = None


class TeamSummaryResponse(BaseModel):
    total_members: int = 0
    active_members: int = 0
    pending_invitations: int = 0
    admins: int = 0
    operators: int = 0
    analysts: int = 0
    developers: int = 0
    viewers: int = 0
    is_last_owner: bool = False


class InviteMemberRequest(BaseModel):
    email: str = Field(..., min_length=1)
    role: str = Field(default="viewer")
    workspace_id: str | None = None


class UpdateRoleRequest(BaseModel):
    role: str


class GrantAccessRequest(BaseModel):
    workspace_id: str
    member_id: str
    access_level: str = "read"


class AssignAgentRequest(BaseModel):
    workspace_id: str
    agent_id: str
    member_id: str | None = None
    assignment_role: str = "observer"
