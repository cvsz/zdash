from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

RealtimeCategory = Literal["system", "trading", "risk", "scheduler", "content", "iot", "admin", "audit"]
RealtimeSeverity = Literal["info", "warning", "critical"]
RealtimeChannel = Literal["events", "risk", "scheduler", "content"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RealtimeEventEnvelope(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=utc_now_iso)
    category: RealtimeCategory = "system"
    type: str
    severity: RealtimeSeverity = "info"
    source: str = "system"
    message: str = ""
    data: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        if not self.message and isinstance(self.data.get("message"), str):
            self.message = self.data["message"]
        if not self.payload:
            self.payload = dict(self.data)
        if not self.data:
            self.data = dict(self.payload)


class RealtimeControlMessage(BaseModel):
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)
