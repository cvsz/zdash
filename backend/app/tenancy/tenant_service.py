from __future__ import annotations

from app.auth.models import AuthSession
from app.core.config import get_settings
from app.tenancy.models import (
    MemberCreateRequest,
    Organization,
    OrganizationCreateRequest,
    OrganizationMember,
    OrganizationUpdateRequest,
    Workspace,
    WorkspaceCreateRequest,
    WorkspaceMember,
    WorkspaceUpdateRequest,
    normalize_slug,
)
from app.tenancy.repositories import get_tenancy_repository
from app.tenancy.tenant_context import TenantContext


class TenantService:
    def __init__(self) -> None:
        self.repository = get_tenancy_repository()

    def ensure_bootstrap(self, user_id: str = "dev-user") -> tuple[Organization, Workspace]:
        settings = get_settings()
        return self.repository.bootstrap_defaults(
            organization_name=settings.default_org_name,
            workspace_name=settings.default_workspace_name,
            owner_user_id=user_id,
        )

    def resolve_context(
        self,
        user: AuthSession,
        *,
        organization_id: str | None,
        workspace_id: str | None,
        source: str,
    ) -> TenantContext:
        default_org, default_workspace = self.ensure_bootstrap(user.username)

        resolved_organization_id = (organization_id or "").strip() or default_org.id
        resolved_workspace_id = (workspace_id or "").strip() or default_workspace.id
        workspace = self.repository.get_workspace(resolved_workspace_id)
        if workspace is None:
            raise LookupError("workspace not found")

        if not organization_id:
            resolved_organization_id = workspace.organization_id

        organization = self.repository.get_organization(resolved_organization_id)
        if organization is None:
            raise LookupError("organization not found")
        if workspace.organization_id != organization.id:
            raise PermissionError("workspace does not belong to organization")

        settings = get_settings()
        if settings.multi_tenant_enabled and user.role != "admin":
            allowed_orgs = self.repository.user_organization_ids(user.username)
            allowed_workspaces = self.repository.user_workspace_ids(user.username)
            if organization.id not in allowed_orgs or workspace.id not in allowed_workspaces:
                raise PermissionError("cross-tenant access forbidden")

        return TenantContext(
            organization_id=organization.id,
            workspace_id=workspace.id,
            user_id=user.username,
            user_role=user.role,
            source=source,
        )

    def list_accessible_organizations(self, user: AuthSession) -> list[Organization]:
        self.ensure_bootstrap(user.username)
        if user.role == "admin":
            return self.repository.list_organizations()
        allowed = self.repository.user_organization_ids(user.username)
        return [
            organization
            for organization in self.repository.list_organizations()
            if organization.id in allowed
        ]

    def get_organization(self, organization_id: str) -> Organization | None:
        return self.repository.get_organization(organization_id)

    def create_organization(
        self,
        payload: OrganizationCreateRequest,
        owner: AuthSession,
    ) -> Organization:
        slug = payload.slug or normalize_slug(payload.name)
        organization = Organization(
            name=payload.name.strip(),
            slug=slug,
            owner_user_id=owner.username,
        )
        created = self.repository.create_organization(organization)
        self.repository.add_organization_member(
            OrganizationMember(
                organization_id=created.id,
                user_id=owner.username,
                role="admin",
                status="active",
            )
        )
        return created

    def update_organization(
        self,
        organization_id: str,
        payload: OrganizationUpdateRequest,
    ) -> Organization | None:
        return self.repository.update_organization(
            organization_id,
            name=payload.name.strip() if payload.name else None,
            status=payload.status,
        )

    def list_workspaces(self, organization_id: str) -> list[Workspace]:
        return self.repository.list_workspaces(organization_id)

    def create_workspace(
        self,
        organization_id: str,
        payload: WorkspaceCreateRequest,
        actor: AuthSession,
    ) -> Workspace:
        organization = self.repository.get_organization(organization_id)
        if organization is None:
            raise LookupError("organization not found")
        workspace = Workspace(
            organization_id=organization.id,
            name=payload.name.strip(),
            slug=payload.slug or normalize_slug(payload.name),
            environment=payload.environment,
        )
        created = self.repository.create_workspace(workspace)
        self.repository.add_workspace_member(
            WorkspaceMember(
                workspace_id=created.id,
                user_id=actor.username,
                role="admin",
                status="active",
            )
        )
        return created

    def update_workspace(
        self,
        workspace_id: str,
        payload: WorkspaceUpdateRequest,
    ) -> Workspace | None:
        return self.repository.update_workspace(
            workspace_id,
            name=payload.name.strip() if payload.name else None,
            status=payload.status,
            environment=payload.environment,
        )

    def get_workspace(self, workspace_id: str) -> Workspace | None:
        return self.repository.get_workspace(workspace_id)

    def add_organization_member(
        self,
        organization_id: str,
        payload: MemberCreateRequest,
    ) -> OrganizationMember:
        organization = self.repository.get_organization(organization_id)
        if organization is None:
            raise LookupError("organization not found")
        return self.repository.add_organization_member(
            OrganizationMember(
                organization_id=organization.id,
                user_id=payload.user_id.strip(),
                role=payload.role,
                status=payload.status,
            )
        )

    def add_workspace_member(
        self,
        workspace_id: str,
        payload: MemberCreateRequest,
    ) -> WorkspaceMember:
        workspace = self.repository.get_workspace(workspace_id)
        if workspace is None:
            raise LookupError("workspace not found")
        return self.repository.add_workspace_member(
            WorkspaceMember(
                workspace_id=workspace.id,
                user_id=payload.user_id.strip(),
                role=payload.role,
                status=payload.status,
            )
        )

    def is_organization_admin(self, organization_id: str, user: AuthSession) -> bool:
        if user.role == "admin":
            return True
        organization = self.repository.get_organization(organization_id)
        if organization and organization.owner_user_id == user.username:
            return True
        members = self.repository.list_organization_members(organization_id)
        return any(
            member.user_id == user.username and member.role == "admin"
            for member in members
        )

    def can_access_workspace(self, workspace_id: str, user: AuthSession) -> bool:
        if user.role == "admin":
            return True
        allowed = self.repository.user_workspace_ids(user.username)
        return workspace_id in allowed


service = TenantService()
