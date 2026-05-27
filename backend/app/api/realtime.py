from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.responses import ok
from app.realtime import bind_realtime_loop, get_realtime_broadcaster, get_realtime_connection_manager, get_realtime_heartbeat
from app.realtime.events import build_event_envelope
from app.realtime.mock_streams import start_mock_stream_if_enabled

router = APIRouter(prefix="/api/realtime", tags=["realtime"])


@router.websocket("/ws")
async def ws_realtime(websocket: WebSocket) -> None:
    bind_realtime_loop(asyncio.get_running_loop())
    start_mock_stream_if_enabled()
    manager = get_realtime_connection_manager()
    broadcaster = get_realtime_broadcaster()
    heartbeat = get_realtime_heartbeat()
    heartbeat.start()
    client_id = await manager.connect("events", websocket)
    try:
        for payload in broadcaster.recent_events("events", limit=150):
            await websocket.send_json(payload)
        while True:
            message = await websocket.receive_text()
            msg_type = _parse_message_type(message)
            if msg_type in {"ping", "system.ping"}:
                await websocket.send_json(build_event_envelope(event_type="system.pong", source="realtime.gateway", payload={"client_id": client_id}).model_dump(mode="json"))
    except WebSocketDisconnect:
        return
    finally:
        await manager.disconnect("events", client_id)




@router.websocket("/ws/events")
async def ws_events_compat(websocket: WebSocket) -> None:
    await ws_realtime(websocket)

@router.get("/status")
def realtime_status() -> dict:
    return ok({"connections": get_realtime_connection_manager().snapshot()})


@router.get("/events")
def realtime_events(limit: int = Query(default=100, ge=1, le=500)) -> dict:
    events = get_realtime_broadcaster().recent_events("events", limit=limit)
    return ok({"events": events, "count": len(events), "max_retained": 500})


@router.post("/mock-event")
async def mock_event(payload: dict) -> dict:
    envelope = build_event_envelope(
        event_type=str(payload.get("type", "system.mock")),
        source=str(payload.get("source", "mock.api")),
        severity=str(payload.get("severity", "info")),  # type: ignore[arg-type]
        message=str(payload.get("message", "Mock event posted")),
        payload=dict(payload.get("data", {})),
    )
    event = await get_realtime_broadcaster().apublish(envelope)
    return ok({"event": event})


def _parse_message_type(raw_message: str) -> str:
    trimmed = raw_message.strip()
    if trimmed.startswith("{"):
        try:
            parsed = json.loads(trimmed)
            if isinstance(parsed, dict):
                return str(parsed.get("type", "")).strip().lower()
        except json.JSONDecodeError:
            return ""
    return trimmed.lower()
