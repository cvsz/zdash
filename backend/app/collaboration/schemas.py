from __future__ import annotations
from datetime import datetime, timezone
from pydantic import BaseModel, Field

PRESENCE_STATES = {"online","idle","offline","viewing","editing","reviewing","approving"}

class PresenceUpdate(BaseModel):
    workspace_id: str
    current_page: str | None = None
    current_module: str | None = None
    state: str = "online"
    session_id: str

class PresenceRecord(PresenceUpdate):
    user_id: str
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NoteCreate(BaseModel):
    workspace_id: str
    module: str
    entity_id: str
    body: str

class NoteRecord(NoteCreate):
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    resolved: bool = False
    deleted: bool = False

class TimelineEvent(BaseModel):
    id: str
    workspace_id: str
    event_type: str
    actor: str
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = Field(default_factory=dict)
