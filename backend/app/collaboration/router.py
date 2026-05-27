from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from app.auth.dependencies import get_current_user
from app.auth.jwt import decode_token
from app.auth.models import AuthSession
from app.core.config import get_settings
from app.core.responses import ok

from .schemas import NoteCreate, PresenceUpdate
from .service import service

router = APIRouter(prefix="/api/collaboration", tags=["collaboration"])


@router.get("/presence")
def get_presence(workspace_id: str, _: AuthSession = Depends(get_current_user)):
    return ok({"items": [p.model_dump(mode="json") for p in service.list_presence(workspace_id)]})


@router.post("/presence")
def post_presence(payload: PresenceUpdate, user: AuthSession = Depends(get_current_user)):
    return ok({"item": service.upsert_presence(user.username, payload).model_dump(mode="json")})


@router.get("/notes")
def get_notes(workspace_id: str, _: AuthSession = Depends(get_current_user)):
    return ok({"items": [n.model_dump(mode="json") for n in service.list_notes(workspace_id)]})


@router.post("/notes")
def post_notes(payload: NoteCreate, user: AuthSession = Depends(get_current_user)):
    return ok({"item": service.create_note(user.username, payload).model_dump(mode="json")})


@router.patch("/notes/{note_id}/resolve")
def resolve_note(note_id: str, workspace_id: str, user: AuthSession = Depends(get_current_user)):
    note = service.resolve_note(workspace_id, note_id, user.username)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return ok({"item": note.model_dump(mode="json")})


@router.get("/timeline")
def timeline(
    workspace_id: str,
    cursor: int = 0,
    limit: int = Query(50, ge=1, le=200),
    event_type: str | None = None,
    _: AuthSession = Depends(get_current_user),
):
    items, next_cursor = service.list_timeline(workspace_id, cursor, limit, event_type)
    return ok({"items": [i.model_dump(mode="json") for i in items], "next_cursor": next_cursor})


def _extract_token_from_subprotocol_header(raw_header: str | None) -> str | None:
    if not raw_header:
        return None
    parts = [part.strip() for part in raw_header.split(",") if part.strip()]
    if not parts:
        return None
    if parts[0].lower() == "bearer" and len(parts) > 1:
        return parts[1]
    for part in parts:
        if part.lower().startswith("bearer "):
            candidate = part.split(" ", 1)[1].strip()
            if candidate:
                return candidate
    for part in parts:
        if part.count(".") == 2:
            return part
    return None


def _extract_websocket_token(websocket: WebSocket) -> str | None:
    query_token = str(websocket.query_params.get("token", "")).strip()
    if query_token:
        return query_token
    return _extract_token_from_subprotocol_header(
        websocket.headers.get("sec-websocket-protocol")
    )


def _authenticate_websocket(websocket: WebSocket) -> AuthSession | None:
    settings = get_settings()
    if not settings.auth_enabled:
        return AuthSession(username="dev-user", role="admin")

    token = _extract_websocket_token(websocket)
    if not token:
        return None

    try:
        payload = decode_token(token)
    except ValueError:
        return None

    if payload.get("type") != "access":
        return None

    username = str(payload.get("sub", "")).strip()
    role = str(payload.get("role", "viewer")).strip() or "viewer"
    if not username:
        return None

    return AuthSession(username=username, role=role)


@router.websocket("/ws/collaboration/{workspace_id}")
async def ws_collab(websocket: WebSocket, workspace_id: str):
    auth_session = _authenticate_websocket(websocket)
    if auth_session is None:
        await websocket.accept()
        await websocket.close(code=1008, reason="Unauthorized")
        return

    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            if msg.get("type") == "presence.update":
                await websocket.send_json({"ok": True, "type": "ack"})
            elif msg.get("type") == "timeline.subscribe":
                items, _ = service.list_timeline(workspace_id)
                await websocket.send_json(
                    {
                        "type": "timeline.snapshot",
                        "items": [i.model_dump(mode="json") for i in items],
                    }
                )
    except (WebSocketDisconnect, json.JSONDecodeError):
        return
