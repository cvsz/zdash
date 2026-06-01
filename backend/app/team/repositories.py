from sqlalchemy import select
from sqlalchemy.orm import Session

from app.team.models import (
    TeamAgentAssignment,
    TeamInvitation,
    TeamMember,
    TeamWorkspaceAccess,
)


class TeamMemberRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> TeamMember:
        row = TeamMember(**kwargs)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def get_by_id(self, member_id: str) -> TeamMember | None:
        q = select(TeamMember).where(TeamMember.id == member_id)
        return self.db.execute(q).scalar_one_or_none()

    def get_by_org(self, org_id: str, member_id: str) -> TeamMember | None:
        q = select(TeamMember).where(
            TeamMember.organization_id == org_id, TeamMember.id == member_id
        )
        return self.db.execute(q).scalar_one_or_none()

    def get_by_org_and_email(self, org_id: str, email: str) -> TeamMember | None:
        q = select(TeamMember).where(
            TeamMember.organization_id == org_id, TeamMember.email == email
        )
        return self.db.execute(q).scalar_one_or_none()

    def list_by_org(self, org_id: str) -> list[TeamMember]:
        q = (
            select(TeamMember)
            .where(TeamMember.organization_id == org_id)
            .order_by(TeamMember.created_at.desc())
        )
        return list(self.db.execute(q).scalars().all())

    def list_by_org_and_workspace(
        self, org_id: str, workspace_id: str
    ) -> list[TeamMember]:
        q = (
            select(TeamMember)
            .where(
                TeamMember.organization_id == org_id,
                TeamMember.workspace_id == workspace_id,
            )
            .order_by(TeamMember.created_at.desc())
        )
        return list(self.db.execute(q).scalars().all())

    def update(self, member_id: str, **kwargs) -> TeamMember | None:
        row = self.get_by_id(member_id)
        if not row:
            return None
        for key, value in kwargs.items():
            setattr(row, key, value)
        self.db.commit()
        self.db.refresh(row)
        return row

    def delete(self, member_id: str) -> bool:
        row = self.get_by_id(member_id)
        if not row:
            return False
        self.db.delete(row)
        self.db.commit()
        return True

    def count_by_org(self, org_id: str) -> int:
        q = select(TeamMember).where(TeamMember.organization_id == org_id)
        return len(list(self.db.execute(q).scalars().all()))

    def count_by_org_and_role(self, org_id: str, role: str) -> int:
        q = select(TeamMember).where(
            TeamMember.organization_id == org_id, TeamMember.role == role
        )
        return len(list(self.db.execute(q).scalars().all()))

    def count_by_org_and_status(self, org_id: str, status: str) -> int:
        q = select(TeamMember).where(
            TeamMember.organization_id == org_id, TeamMember.status == status
        )
        return len(list(self.db.execute(q).scalars().all()))


class TeamInvitationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> TeamInvitation:
        row = TeamInvitation(**kwargs)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def get_by_id(self, invitation_id: str) -> TeamInvitation | None:
        q = select(TeamInvitation).where(TeamInvitation.id == invitation_id)
        return self.db.execute(q).scalar_one_or_none()

    def get_by_org(self, org_id: str, invitation_id: str) -> TeamInvitation | None:
        q = select(TeamInvitation).where(
            TeamInvitation.organization_id == org_id,
            TeamInvitation.id == invitation_id,
        )
        return self.db.execute(q).scalar_one_or_none()

    def get_by_org_and_email(self, org_id: str, email: str) -> TeamInvitation | None:
        q = select(TeamInvitation).where(
            TeamInvitation.organization_id == org_id, TeamInvitation.email == email
        )
        return self.db.execute(q).scalar_one_or_none()

    def list_by_org(self, org_id: str) -> list[TeamInvitation]:
        q = (
            select(TeamInvitation)
            .where(TeamInvitation.organization_id == org_id)
            .order_by(TeamInvitation.created_at.desc())
        )
        return list(self.db.execute(q).scalars().all())

    def list_by_org_and_workspace(
        self, org_id: str, workspace_id: str
    ) -> list[TeamInvitation]:
        q = (
            select(TeamInvitation)
            .where(
                TeamInvitation.organization_id == org_id,
                TeamInvitation.workspace_id == workspace_id,
            )
            .order_by(TeamInvitation.created_at.desc())
        )
        return list(self.db.execute(q).scalars().all())

    def update(self, invitation_id: str, **kwargs) -> TeamInvitation | None:
        row = self.get_by_id(invitation_id)
        if not row:
            return None
        for key, value in kwargs.items():
            setattr(row, key, value)
        self.db.commit()
        self.db.refresh(row)
        return row

    def delete(self, invitation_id: str) -> bool:
        row = self.get_by_id(invitation_id)
        if not row:
            return False
        self.db.delete(row)
        self.db.commit()
        return True


class TeamWorkspaceAccessRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> TeamWorkspaceAccess:
        row = TeamWorkspaceAccess(**kwargs)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def get_by_id(self, access_id: str) -> TeamWorkspaceAccess | None:
        q = select(TeamWorkspaceAccess).where(TeamWorkspaceAccess.id == access_id)
        return self.db.execute(q).scalar_one_or_none()

    def list_by_org_and_workspace(
        self, org_id: str, workspace_id: str
    ) -> list[TeamWorkspaceAccess]:
        q = (
            select(TeamWorkspaceAccess)
            .where(
                TeamWorkspaceAccess.organization_id == org_id,
                TeamWorkspaceAccess.workspace_id == workspace_id,
            )
            .order_by(TeamWorkspaceAccess.created_at.desc())
        )
        return list(self.db.execute(q).scalars().all())

    def list_by_member(self, member_id: str) -> list[TeamWorkspaceAccess]:
        q = (
            select(TeamWorkspaceAccess)
            .where(TeamWorkspaceAccess.member_id == member_id)
            .order_by(TeamWorkspaceAccess.created_at.desc())
        )
        return list(self.db.execute(q).scalars().all())

    def update(self, access_id: str, **kwargs) -> TeamWorkspaceAccess | None:
        row = self.get_by_id(access_id)
        if not row:
            return None
        for key, value in kwargs.items():
            setattr(row, key, value)
        self.db.commit()
        self.db.refresh(row)
        return row

    def delete(self, access_id: str) -> bool:
        row = self.get_by_id(access_id)
        if not row:
            return False
        self.db.delete(row)
        self.db.commit()
        return True


class TeamAgentAssignmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> TeamAgentAssignment:
        row = TeamAgentAssignment(**kwargs)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def get_by_id(self, assignment_id: str) -> TeamAgentAssignment | None:
        q = select(TeamAgentAssignment).where(TeamAgentAssignment.id == assignment_id)
        return self.db.execute(q).scalar_one_or_none()

    def list_by_org(self, org_id: str) -> list[TeamAgentAssignment]:
        q = (
            select(TeamAgentAssignment)
            .where(TeamAgentAssignment.organization_id == org_id)
            .order_by(TeamAgentAssignment.created_at.desc())
        )
        return list(self.db.execute(q).scalars().all())

    def list_by_org_and_workspace(
        self, org_id: str, workspace_id: str
    ) -> list[TeamAgentAssignment]:
        q = (
            select(TeamAgentAssignment)
            .where(
                TeamAgentAssignment.organization_id == org_id,
                TeamAgentAssignment.workspace_id == workspace_id,
            )
            .order_by(TeamAgentAssignment.created_at.desc())
        )
        return list(self.db.execute(q).scalars().all())

    def list_by_agent(self, agent_id: str) -> list[TeamAgentAssignment]:
        q = (
            select(TeamAgentAssignment)
            .where(TeamAgentAssignment.agent_id == agent_id)
            .order_by(TeamAgentAssignment.created_at.desc())
        )
        return list(self.db.execute(q).scalars().all())

    def delete(self, assignment_id: str) -> bool:
        row = self.get_by_id(assignment_id)
        if not row:
            return False
        self.db.delete(row)
        self.db.commit()
        return True
