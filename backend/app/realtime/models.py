from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

RealtimeSeverity = Literal["info", "warning", "critical"]


class RealtimeEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    type: str
    source: str
    severity: RealtimeSeverity = "info"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = Field(default_factory=dict)
