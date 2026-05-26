from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

IoTActionName = Literal['status', 'turn_on', 'turn_off', 'power_cycle']


class IoTAction(BaseModel):
    device_alias: str = 'zdash-power-node'
    action: IoTActionName
    confirmation: bool = False
    payload: dict[str, Any] = Field(default_factory=dict)


class IoTActionResult(BaseModel):
    ok: bool
    dry_run: bool
    device_alias: str
    action: IoTActionName
    message: str
    output: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IoTActionRequest(IoTAction):
    """Backward-compatible alias used by earlier API layer."""


class IoTPowerCycleRequest(BaseModel):
    device_alias: str = 'zdash-power-node'
    confirmation: bool = False
