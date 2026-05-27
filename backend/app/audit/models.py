from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuditLogCreate(BaseModel):
    actor_user_id: str = ""
    actor_email: str = ""
    action: str = Field(min_length=1)
    resource_type: str = ""
    resource_id: str = ""
    result: str = "success"
    ip_address: str = ""
    user_agent: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditLogItem(BaseModel):
    id: str
    actor_user_id: str
    actor_email: str
    action: str
    resource_type: str
    resource_id: str
    result: str
    ip_address: str
    user_agent: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
