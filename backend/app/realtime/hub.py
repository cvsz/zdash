from __future__ import annotations

from collections import deque
from uuid import uuid4

from app.realtime.broadcast import broadcast_event
from app.realtime.manager import get_realtime_connection_manager
from app.realtime.models import RealtimeEnvelope


class EventHub:
    def __init__(self, replay_limit: int = 250) -> None:
        self.replay_limit = replay_limit
        self._replay: deque[dict] = deque(maxlen=replay_limit)

    async def broadcast(self, event_type: str, source: str, payload: dict, severity: str = "info") -> dict:
        event = RealtimeEnvelope(
            id=f"evt_{uuid4().hex[:12]}",
            type=event_type,
            timestamp=payload.get("timestamp") or payload.get("ts") or __import__("datetime").datetime.utcnow().isoformat() + "Z",
            source=source,
            severity=severity,
            payload=payload,
        ).model_dump(mode="json")
        self._replay.append(event)
        await broadcast_event(event_type, source, payload, severity)
        await get_realtime_connection_manager().broadcast("events", event)
        return event

    def replay(self, limit: int = 100) -> list[dict]:
        return list(self._replay)[-max(1, min(limit, self.replay_limit)) :]


_event_hub: EventHub | None = None


def get_event_hub() -> EventHub:
    global _event_hub
    if _event_hub is None:
        _event_hub = EventHub()
    return _event_hub
