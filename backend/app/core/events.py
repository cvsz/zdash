from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from threading import Lock
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str
    source: str
    message: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class EventBus:
    def __init__(self, max_events: int = 1000) -> None:
        self._events: deque[Event] = deque(maxlen=max_events)
        self._lock = Lock()

    def emit(self, event_type: str, source: str, message: str, payload: dict[str, Any] | None = None) -> Event:
        event = Event(type=event_type, source=source, message=message, payload=payload or {})
        with self._lock:
            self._events.append(event)
        return event

    def list_events(self, limit: int = 100) -> list[Event]:
        safe_limit = max(1, min(limit, 1000))
        with self._lock:
            items = list(self._events)
        return items[-safe_limit:]


event_bus = EventBus()
