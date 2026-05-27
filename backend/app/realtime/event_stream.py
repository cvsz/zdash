from __future__ import annotations

from typing import Any

from app.realtime.broadcaster import get_realtime_broadcaster
from app.realtime.schemas import RealtimeEventEnvelope


def push(event: dict[str, Any]) -> None:
    envelope = RealtimeEventEnvelope.model_validate(event)
    get_realtime_broadcaster().publish(envelope)


def recent(limit: int = 100) -> list[dict[str, Any]]:
    return get_realtime_broadcaster().recent_events("events", limit=limit)
