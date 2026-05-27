from __future__ import annotations
import json
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from app.auth.dependencies import get_current_user
from app.auth.models import AuthSession
from app.core.responses import ok
from .schemas import NoteCreate, PresenceUpdate
from .service import service

router = APIRouter(prefix="/api/collaboration", tags=["collaboration"])

@router.get("/presence")
def get_presence(workspace_id: str, _: AuthSession = Depends(get_current_user)):
    return ok({"items": [p.model_dump(mode='json') for p in service.list_presence(workspace_id)]})

@router.post("/presence")
def post_presence(payload: PresenceUpdate, user: AuthSession = Depends(get_current_user)):
    return ok({"item": service.upsert_presence(user.username, payload).model_dump(mode='json')})

@router.get("/notes")
def get_notes(workspace_id: str, _: AuthSession = Depends(get_current_user)):
    return ok({"items": [n.model_dump(mode='json') for n in service.list_notes(workspace_id)]})

@router.post("/notes")
def post_notes(payload: NoteCreate, user: AuthSession = Depends(get_current_user)):
    return ok({"item": service.create_note(user.username, payload).model_dump(mode='json')})

@router.patch("/notes/{note_id}/resolve")
def resolve_note(note_id: str, workspace_id: str, user: AuthSession = Depends(get_current_user)):
    note = service.resolve_note(workspace_id, note_id, user.username)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return ok({"item": note.model_dump(mode='json')})

@router.get("/timeline")
def timeline(workspace_id: str, cursor: int = 0, limit: int = Query(50, ge=1, le=200), event_type: str | None = None, _: AuthSession = Depends(get_current_user)):
    items, next_cursor = service.list_timeline(workspace_id, cursor, limit, event_type)
    return ok({"items": [i.model_dump(mode='json') for i in items], "next_cursor": next_cursor})

@router.websocket("/ws/collaboration/{workspace_id}")
async def ws_collab(websocket: WebSocket, workspace_id: str):
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            if msg.get("type") == "presence.update":
                await websocket.send_json({"ok": True, "type": "ack"})
            elif msg.get("type") == "timeline.subscribe":
                items, _ = service.list_timeline(workspace_id)
                await websocket.send_json({"type": "timeline.snapshot", "items": [i.model_dump(mode='json') for i in items]})
    except (WebSocketDisconnect, json.JSONDecodeError):
        return
