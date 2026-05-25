from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from .models import WaitlistEntry, WaitlistStatus


class WaitlistService:
    def __init__(self) -> None:
        self._entries: dict[str, WaitlistEntry] = {}

    def join_waitlist(self, request: dict) -> WaitlistEntry:
        for e in self._entries.values():
            if e.email == request["email"]:
                return e
        now = datetime.now(timezone.utc)
        entry = WaitlistEntry(id=str(uuid4()), created_at=now, updated_at=now, **request)
        self._entries[entry.id] = entry
        return entry

    def list_entries(self) -> list[WaitlistEntry]:
        return list(self._entries.values())

    def update_status(self, entry_id: str, status: WaitlistStatus) -> WaitlistEntry:
        entry = self._entries[entry_id]
        entry.status = status
        entry.updated_at = datetime.now(timezone.utc)
        return entry
