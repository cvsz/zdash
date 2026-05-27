from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class RealtimeEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{uuid4().hex[:12]}")
    type: str
    source: str
    severity: str = "info"
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RealtimeEnvelope(BaseModel):
    id: str = Field(pattern=r"^evt_")
    type: str
    timestamp: str
    source: str
    severity: str = "info"
    payload: dict = Field(default_factory=dict)


class PresenceRecord(BaseModel):
    operator: str
    role: str
    connected_at: str
    status: str = "online"
