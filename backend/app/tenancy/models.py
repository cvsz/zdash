from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

TenantStatus = Literal["active", "suspended", "archived"]
WorkspaceEnvironment = Literal["development", "staging", "production", "simulation"]
MemberRole = Literal["admin", "operator", "analyst", "viewer"]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def normalize_slug(value: str) -> str:
    lowered = value.strip().lower().replace("_", "-").replace(" ", "-")
    return "-".join(part for part in lowered.split("-") if part)


class Organization(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("org"))
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=120)
    owner_user_id: str = Field(min_length=1, max_length=120)
    status: TenantStatus = "active"
    created_at: str = Field(default_factory=now_utc)
    updated_at: str = Field(default_factory=now_utc)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        normalized = normalize_slug(value)
        if not normalized:
            raise ValueError("slug is required")
        return normalized


class Workspace(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("ws"))
    organization_id: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=120)
    environment: WorkspaceEnvironment = "development"
    status: TenantStatus = "active"
    created_at: str = Field(default_factory=now_utc)
    updated_at: str = Field(default_factory=now_utc)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        normalized = normalize_slug(value)
        if not normalized:
            raise ValueError("slug is required")
        return normalized


class OrganizationMember(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("org_member"))
    organization_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    role: MemberRole = "viewer"
    status: TenantStatus = "active"
    created_at: str = Field(default_factory=now_utc)
    updated_at: str = Field(default_factory=now_utc)


class WorkspaceMember(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("ws_member"))
    workspace_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    role: MemberRole = "viewer"
    status: TenantStatus = "active"
    created_at: str = Field(default_factory=now_utc)
    updated_at: str = Field(default_factory=now_utc)


class OrganizationCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str | None = Field(default=None, max_length=120)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_slug(value)


class OrganizationUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    status: TenantStatus | None = None


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str | None = Field(default=None, max_length=120)
    environment: WorkspaceEnvironment = "development"

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_slug(value)


class WorkspaceUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    status: TenantStatus | None = None
    environment: WorkspaceEnvironment | None = None


class MemberCreateRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=120)
    role: MemberRole = "viewer"
    status: TenantStatus = "active"
