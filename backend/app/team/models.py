from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _id() -> str:
    return str(uuid4())


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TeamMember(Base, Timestamped):
    __tablename__ = "team_members"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    organization_id: Mapped[str] = mapped_column(String, index=True)
    workspace_id: Mapped[str | None] = mapped_column(String, nullable=True)
    user_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    email: Mapped[str] = mapped_column(String, index=True)
    display_name: Mapped[str] = mapped_column(String, default="")
    role: Mapped[str] = mapped_column(String, default="viewer")
    status: Mapped[str] = mapped_column(String, default="active")
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class TeamInvitation(Base, Timestamped):
    __tablename__ = "team_invitations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    organization_id: Mapped[str] = mapped_column(String, index=True)
    workspace_id: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, index=True)
    role: Mapped[str] = mapped_column(String, default="viewer")
    token_hash: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="pending")
    invited_by: Mapped[str] = mapped_column(String, default="")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class TeamWorkspaceAccess(Base, Timestamped):
    __tablename__ = "team_workspace_access"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    organization_id: Mapped[str] = mapped_column(String, index=True)
    workspace_id: Mapped[str] = mapped_column(String, index=True)
    member_id: Mapped[str] = mapped_column(String, index=True)
    access_level: Mapped[str] = mapped_column(String, default="read")


class TeamAgentAssignment(Base, Timestamped):
    __tablename__ = "team_agent_assignments"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    organization_id: Mapped[str] = mapped_column(String, index=True)
    workspace_id: Mapped[str] = mapped_column(String, index=True)
    member_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    agent_id: Mapped[str] = mapped_column(String, index=True)
    assignment_role: Mapped[str] = mapped_column(String, default="observer")
