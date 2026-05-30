from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.responses import ok
from app.realtime import bind_realtime_loop, get_realtime_broadcaster, get_realtime_connection_manager, get_realtime_heartbeat
from app.realtime.events import build_event_envelope
from app.realtime.mock_streams import start_mock_stream_if_enabled
from app.billing.entitlement_service import check_feature
from app.billing.quota_service import consume
from app.core.config import settings

router = APIRouter(prefix="/api/realtime", tags=["realtime"])


@router.websocket("/ws")
async def ws_realtime(websocket: WebSocket) -> None:
    org_id = websocket.headers.get(settings.tenant_header_name, "default")
    ws_id = websocket.headers.get(settings.workspace_header_name, "default")
    
    if settings.billing_enabled:
        dec = check_feature(org_id, "feature.realtime_stream")
        if not dec.allowed and settings.billing_fail_closed:
            await websocket.close(code=4003, reason="FEATURE_NOT_ENTITLED")
            return
            
        quota = consume(org_id, ws_id, "realtime_connections")
        if not quota.allowed and settings.usage_enforcement_enabled:
            await websocket.close(code=4002, reason="QUOTA_EXCEEDED")
            return

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
    await ws_channel(websocket, "events")


@router.websocket("/ws/{channel}")
async def ws_channel(websocket: WebSocket, channel: str) -> None:
    allowed_channels = {"events", "risk", "scheduler", "content"}
    if channel not in allowed_channels:
        await websocket.close(code=4003, reason="CHANNEL_NOT_ALLOWED")
        return

    org_id = websocket.headers.get(settings.tenant_header_name, "default")
    ws_id = websocket.headers.get(settings.workspace_header_name, "default")

    if settings.billing_enabled:
        dec = check_feature(org_id, "feature.realtime_stream")
        if not dec.allowed and settings.billing_fail_closed:
            await websocket.close(code=4003, reason="FEATURE_NOT_ENTITLED")
            return

        quota = consume(org_id, ws_id, "realtime_connections")
        if not quota.allowed and settings.usage_enforcement_enabled:
            await websocket.close(code=4002, reason="QUOTA_EXCEEDED")
            return

    bind_realtime_loop(asyncio.get_running_loop())
    start_mock_stream_if_enabled()
    manager = get_realtime_connection_manager()
    broadcaster = get_realtime_broadcaster()
    heartbeat = get_realtime_heartbeat()
    heartbeat.start()

    client_id = await manager.connect(channel, websocket)
    try:
        for payload in broadcaster.recent_events(channel, limit=150):
            await websocket.send_json(payload)
        while True:
            message = await websocket.receive_text()
            msg_type = _parse_message_type(message)
            if msg_type in {"ping", "system.ping"}:
                await websocket.send_json(
                    build_event_envelope(
                        event_type="system.pong",
                        source="realtime.gateway",
                        payload={"client_id": client_id, "channel": channel},
                    ).model_dump(mode="json")
                )
    except WebSocketDisconnect:
        return
    finally:
        await manager.disconnect(channel, client_id)

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
