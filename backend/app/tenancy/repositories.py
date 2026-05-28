from __future__ import annotations

from threading import Lock

from app.tenancy.models import (
    Organization,
    OrganizationMember,
    Workspace,
    WorkspaceMember,
    now_utc,
)


class TenancyRepository:
    def __init__(self) -> None:
        self._lock = Lock()
        self.organizations: dict[str, Organization] = {}
        self.workspaces: dict[str, Workspace] = {}
        self.organization_members: dict[str, list[OrganizationMember]] = {}
        self.workspace_members: dict[str, list[WorkspaceMember]] = {}
        self.default_organization_id: str | None = None
        self.default_workspace_id: str | None = None

    def reset(self) -> None:
        with self._lock:
            self.organizations.clear()
            self.workspaces.clear()
            self.organization_members.clear()
            self.workspace_members.clear()
            self.default_organization_id = None
            self.default_workspace_id = None

    def bootstrap_defaults(
        self,
        *,
        organization_name: str,
        workspace_name: str,
        owner_user_id: str = "dev-user",
    ) -> tuple[Organization, Workspace]:
        with self._lock:
            if self.default_organization_id and self.default_workspace_id:
                org = self.organizations[self.default_organization_id]
                workspace = self.workspaces[self.default_workspace_id]
                return org, workspace

            org = Organization(
                name=organization_name,
                slug="default-org",
                owner_user_id=owner_user_id,
                status="active",
            )
            workspace = Workspace(
                organization_id=org.id,
                name=workspace_name,
                slug="default-workspace",
                environment="development",
                status="active",
            )
            self.organizations[org.id] = org
            self.workspaces[workspace.id] = workspace
            self.organization_members[org.id] = [
                OrganizationMember(
                    organization_id=org.id,
                    user_id=owner_user_id,
                    role="admin",
                    status="active",
                )
            ]
            self.workspace_members[workspace.id] = [
                WorkspaceMember(
                    workspace_id=workspace.id,
                    user_id=owner_user_id,
                    role="admin",
                    status="active",
                )
            ]
            self.default_organization_id = org.id
            self.default_workspace_id = workspace.id
            return org, workspace

    def list_organizations(self) -> list[Organization]:
        with self._lock:
            return list(self.organizations.values())

    def get_organization(self, organization_id: str) -> Organization | None:
        with self._lock:
            return self.organizations.get(organization_id)

    def create_organization(self, organization: Organization) -> Organization:
        with self._lock:
            self.organizations[organization.id] = organization
            self.organization_members.setdefault(organization.id, [])
            return organization

    def update_organization(
        self,
        organization_id: str,
        *,
        name: str | None = None,
        status: str | None = None,
    ) -> Organization | None:
        with self._lock:
            item = self.organizations.get(organization_id)
            if item is None:
                return None
            data = item.model_dump()
            if name is not None:
                data["name"] = name
            if status is not None:
                data["status"] = status
            data["updated_at"] = now_utc()
            updated = Organization(**data)
            self.organizations[organization_id] = updated
            return updated

    def list_workspaces(self, organization_id: str) -> list[Workspace]:
        with self._lock:
            return [
                workspace
                for workspace in self.workspaces.values()
                if workspace.organization_id == organization_id
            ]

    def get_workspace(self, workspace_id: str) -> Workspace | None:
        with self._lock:
            return self.workspaces.get(workspace_id)

    def create_workspace(self, workspace: Workspace) -> Workspace:
        with self._lock:
            self.workspaces[workspace.id] = workspace
            self.workspace_members.setdefault(workspace.id, [])
            return workspace

    def update_workspace(
        self,
        workspace_id: str,
        *,
        name: str | None = None,
        status: str | None = None,
        environment: str | None = None,
    ) -> Workspace | None:
        with self._lock:
            item = self.workspaces.get(workspace_id)
            if item is None:
                return None
            data = item.model_dump()
            if name is not None:
                data["name"] = name
            if status is not None:
                data["status"] = status
            if environment is not None:
                data["environment"] = environment
            data["updated_at"] = now_utc()
            updated = Workspace(**data)
            self.workspaces[workspace_id] = updated
            return updated

    def add_organization_member(self, member: OrganizationMember) -> OrganizationMember:
        with self._lock:
            members = self.organization_members.setdefault(member.organization_id, [])
            for index, existing in enumerate(members):
                if existing.user_id == member.user_id:
                    data = member.model_dump()
                    data["id"] = existing.id
                    data["created_at"] = existing.created_at
                    data["updated_at"] = now_utc()
                    updated = OrganizationMember(**data)
                    members[index] = updated
                    return updated
            members.append(member)
            return member

    def add_workspace_member(self, member: WorkspaceMember) -> WorkspaceMember:
        with self._lock:
            members = self.workspace_members.setdefault(member.workspace_id, [])
            for index, existing in enumerate(members):
                if existing.user_id == member.user_id:
                    data = member.model_dump()
                    data["id"] = existing.id
                    data["created_at"] = existing.created_at
                    data["updated_at"] = now_utc()
                    updated = WorkspaceMember(**data)
                    members[index] = updated
                    return updated
            members.append(member)
            return member

    def list_organization_members(self, organization_id: str) -> list[OrganizationMember]:
        with self._lock:
            return list(self.organization_members.get(organization_id, []))

    def list_workspace_members(self, workspace_id: str) -> list[WorkspaceMember]:
        with self._lock:
            return list(self.workspace_members.get(workspace_id, []))

    def user_organization_ids(self, user_id: str) -> set[str]:
        with self._lock:
            ids: set[str] = set()
            for organization_id, members in self.organization_members.items():
                if any(member.user_id == user_id and member.status == "active" for member in members):
                    ids.add(organization_id)
            return ids

    def user_workspace_ids(self, user_id: str) -> set[str]:
        with self._lock:
            ids: set[str] = set()
            for workspace_id, members in self.workspace_members.items():
                if any(member.user_id == user_id and member.status == "active" for member in members):
                    ids.add(workspace_id)
            return ids


_repository: TenancyRepository | None = None


def get_tenancy_repository() -> TenancyRepository:
    global _repository
    if _repository is None:
        _repository = TenancyRepository()
    return _repository


def reset_tenancy_repository() -> None:
    global _repository
    _repository = None
