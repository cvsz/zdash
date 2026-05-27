from __future__ import annotations

from app.realtime.models import PresenceRecord


class PresenceStore:
    def __init__(self) -> None:
        self._items: dict[str, PresenceRecord] = {}

    def upsert(self, client_id: str, record: PresenceRecord) -> None:
        self._items[client_id] = record

    def remove(self, client_id: str) -> None:
        self._items.pop(client_id, None)

    def list(self) -> list[PresenceRecord]:
        return list(self._items.values())
