from __future__ import annotations

from app.realtime.broadcaster import get_realtime_broadcaster
from app.realtime.events import build_event_envelope


async def broadcast_event(event_type: str, source: str, payload: dict, severity: str = "info") -> dict:
    event = build_event_envelope(event_type=event_type, source=source, payload=payload, severity=severity)
    return await get_realtime_broadcaster().apublish(event)
