from __future__ import annotations

from pydantic import BaseModel, Field


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
