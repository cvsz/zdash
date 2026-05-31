from __future__ import annotations

from datetime import datetime, UTC
from uuid import uuid4

from app.realtime.hub import get_event_hub


class IncidentService:
    def __init__(self) -> None:
        self._items: dict[str, dict] = {}

    async def create_incident(self, title: str, severity: str, notes: str = "", actor: str = "system") -> dict:
        now = datetime.now(UTC).isoformat()
        item_id = str(uuid4())
        item = {"id": item_id, "title": title, "severity": severity, "status": "open", "created_at": now, "updated_at": now, "acknowledged_by": None, "resolved_by": None, "notes": notes}
        self._items[item_id] = item
        await get_event_hub().broadcast("incident.created", "incident.service", {"incident": item, "actor": actor}, "warning")
        return item

    def list_incidents(self) -> list[dict]:
        return list(self._items.values())

    async def acknowledge_incident(self, incident_id: str, actor: str) -> dict:
        item = self._items[incident_id]
        item["status"] = "acknowledged"
        item["acknowledged_by"] = actor
        item["updated_at"] = datetime.now(UTC).isoformat()
        await get_event_hub().broadcast("incident.updated", "incident.service", {"incident": item, "action": "ack", "actor": actor}, "info")
        return item

    async def resolve_incident(self, incident_id: str, actor: str, notes: str = "") -> dict:
        item = self._items[incident_id]
        item["status"] = "resolved"
        item["resolved_by"] = actor
        item["notes"] = notes or item.get("notes", "")
        item["updated_at"] = datetime.now(UTC).isoformat()
        await get_event_hub().broadcast("incident.updated", "incident.service", {"incident": item, "action": "resolve", "actor": actor}, "warning")
        return item


_service: IncidentService | None = None


def get_incident_service() -> IncidentService:
    global _service
    if _service is None:
        _service = IncidentService()
    return _service


def reset_incident_service() -> None:
    global _service
    _service = None
