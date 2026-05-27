from __future__ import annotations

import html
import re
import uuid
from datetime import datetime, timedelta, timezone

from .schemas import NoteCreate, NoteRecord, PresenceRecord, PresenceUpdate, TimelineEvent

class CollaborationService:
    def __init__(self):
        self.presence: dict[str, dict[str, PresenceRecord]] = {}
        self.notes: dict[str, list[NoteRecord]] = {}
        self.timeline: dict[str, list[TimelineEvent]] = {}
        self.timeout_seconds = 120

    def sanitize_markdown(self, text: str) -> str:
        text = html.escape(text)
        return re.sub(r"javascript:", "", text, flags=re.I)

    def upsert_presence(self, user_id: str, payload: PresenceUpdate) -> PresenceRecord:
        rec = PresenceRecord(**payload.model_dump(), user_id=user_id)
        self.presence.setdefault(payload.workspace_id, {})[payload.session_id] = rec
        return rec

    def list_presence(self, workspace_id: str) -> list[PresenceRecord]:
        now = datetime.now(timezone.utc)
        ws = self.presence.get(workspace_id, {})
        alive = []
        for sid, rec in list(ws.items()):
            if now - rec.last_seen > timedelta(seconds=self.timeout_seconds):
                del ws[sid]
                continue
            alive.append(rec)
        return alive

    def create_note(self, user_id: str, payload: NoteCreate) -> NoteRecord:
        now = datetime.now(timezone.utc)
        note = NoteRecord(id=str(uuid.uuid4()), created_by=user_id, created_at=now, updated_at=now, body=self.sanitize_markdown(payload.body), **payload.model_dump(exclude={"body"}))
        self.notes.setdefault(payload.workspace_id, []).append(note)
        self.add_event(payload.workspace_id, "workspace.note.created", user_id, f"{user_id} created a note", {"note_id": note.id})
        return note

    def resolve_note(self, workspace_id: str, note_id: str, actor: str) -> NoteRecord | None:
        for n in self.notes.get(workspace_id, []):
            if n.id == note_id and not n.deleted:
                n.resolved = True
                n.updated_at = datetime.now(timezone.utc)
                self.add_event(workspace_id, "workspace.note.resolved", actor, f"{actor} resolved a note", {"note_id": note_id})
                return n
        return None

    def list_notes(self, workspace_id: str) -> list[NoteRecord]:
        return [n for n in self.notes.get(workspace_id, []) if not n.deleted]

    def add_event(self, workspace_id: str, event_type: str, actor: str, message: str, metadata: dict | None = None) -> TimelineEvent:
        ev = TimelineEvent(id=str(uuid.uuid4()), workspace_id=workspace_id, event_type=event_type, actor=actor, message=message, metadata=metadata or {})
        self.timeline.setdefault(workspace_id, []).append(ev)
        return ev

    def list_timeline(self, workspace_id: str, cursor: int = 0, limit: int = 50, event_type: str | None = None):
        events = self.timeline.get(workspace_id, [])
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        sliced = events[cursor: cursor + limit]
        return sliced, cursor + len(sliced)

service = CollaborationService()
