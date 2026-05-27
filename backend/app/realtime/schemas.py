from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

RealtimeChannel = Literal["events", "risk", "scheduler", "content"]
RealtimeSeverity = Literal["info", "warning", "danger", "success"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RealtimeEventEnvelope(BaseModel):
    type: str
    timestamp: str = Field(default_factory=utc_now_iso)
    source: str = "system"
    severity: RealtimeSeverity = "info"
    payload: dict[str, Any] = Field(default_factory=dict)


class RealtimeControlMessage(BaseModel):
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)
