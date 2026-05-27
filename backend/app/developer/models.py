from __future__ import annotations
from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, Field


class ApiKeyStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    EXPIRED = "expired"
    REVOKED = "revoked"


class ApiKeyScope(StrEnum):
    READ_HEALTH = "read:health"
    READ_AGENTS = "read:agents"
    READ_LOGS = "read:logs"
    READ_RISK = "read:risk"
    WRITE_RISK_HALT = "write:risk_halt"
    READ_SCHEDULER = "read:scheduler"
    WRITE_SCHEDULER = "write:scheduler"
    READ_BACKTESTING = "read:backtesting"
    WRITE_BACKTESTING = "write:backtesting"
    READ_CONTENT = "read:content"
    WRITE_CONTENT = "write:content"
    READ_INCIDENTS = "read:incidents"
    WRITE_INCIDENTS = "write:incidents"
    READ_DEVELOPER = "read:developer"
    WRITE_WEBHOOKS = "write:webhooks"
    SANDBOX_ALL = "sandbox:all"


class DeveloperApiKey(BaseModel):
    id: str
    organization_id: str
    workspace_id: str
    name: str
    prefix: str
    key_hash: str
    scopes: list[ApiKeyScope]
    status: ApiKeyStatus
    last_used_at: datetime | None = None
    expires_at: datetime | None = None
    created_by: str
    created_at: datetime
    updated_at: datetime
    sandbox_only: bool = True


class ApiKeyCreateRequest(BaseModel):
    name: str
    scopes: list[ApiKeyScope]
    expires_at: datetime | None = None
    sandbox_only: bool = True


class ApiKeyCreatedResponse(BaseModel):
    id: str
    name: str
    raw_key: str
    prefix: str
    scopes: list[ApiKeyScope]
    expires_at: datetime | None = None
    warning: str = Field(default="Store this key now. It will only be shown once.")
