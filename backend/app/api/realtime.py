from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.realtime import (
    bind_realtime_loop,
    get_realtime_broadcaster,
    get_realtime_connection_manager,
    get_realtime_heartbeat,
)
from app.realtime.events import build_event_envelope
from app.realtime.schemas import RealtimeChannel

router = APIRouter(tags=["realtime"])


async def _serve_channel(websocket: WebSocket, channel: RealtimeChannel) -> None:
    bind_realtime_loop(asyncio.get_running_loop())

    manager = get_realtime_connection_manager()
    broadcaster = get_realtime_broadcaster()
    heartbeat = get_realtime_heartbeat()
    heartbeat.start()

    client_id = await manager.connect(channel, websocket)

    await broadcaster.apublish(
        build_event_envelope(
            event_type="system.connected",
            source="realtime.gateway",
            payload={"channel": channel, "client_id": client_id},
            severity="success",
        ),
        channels={"events", channel},
    )

    for payload in broadcaster.recent_events(channel, limit=150):
        await websocket.send_json(payload)

    try:
        while True:
            raw_message = await websocket.receive_text()
            await manager.mark_activity(channel, client_id)

            message_type = _parse_message_type(raw_message)
            if message_type in {"pong", "system.pong", "heartbeat", "system.heartbeat"}:
                await manager.mark_pong(channel, client_id)
                continue

            if message_type in {"ping", "system.ping"}:
                await manager.mark_pong(channel, client_id)
                await websocket.send_json(
                    build_event_envelope(
                        event_type="system.pong",
                        source="realtime.gateway",
                        payload={"channel": channel, "client_id": client_id},
                        severity="info",
                    ).model_dump(mode="json")
                )
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        await broadcaster.apublish(
            build_event_envelope(
                event_type="system.warning",
                source="realtime.gateway",
                payload={
                    "channel": channel,
                    "client_id": client_id,
                    "message": "websocket_receive_error",
                    "error": str(exc),
                },
                severity="warning",
            ),
            channels={"events", channel},
        )
    finally:
        await manager.disconnect(channel, client_id)
        await broadcaster.apublish(
            build_event_envelope(
                event_type="system.disconnected",
                source="realtime.gateway",
                payload={"channel": channel, "client_id": client_id},
                severity="warning",
            ),
            channels={"events", channel},
        )


def _parse_message_type(raw_message: str) -> str:
    trimmed = raw_message.strip()
    if not trimmed:
        return ""

    if trimmed.startswith("{"):
        try:
            payload = json.loads(trimmed)
        except json.JSONDecodeError:
            return ""
        if isinstance(payload, dict):
            message_type = payload.get("type")
            if isinstance(message_type, str):
                return message_type.strip().lower()

    return trimmed.lower()


@router.websocket("/ws/events")
async def ws_events(websocket: WebSocket) -> None:
    await _serve_channel(websocket, "events")


@router.websocket("/ws/risk")
async def ws_risk(websocket: WebSocket) -> None:
    await _serve_channel(websocket, "risk")


@router.websocket("/ws/scheduler")
async def ws_scheduler(websocket: WebSocket) -> None:
    await _serve_channel(websocket, "scheduler")


@router.websocket("/ws/content")
async def ws_content(websocket: WebSocket) -> None:
    await _serve_channel(websocket, "content")


# Backward-compatible endpoint used by earlier realtime placeholders.
@router.websocket("/api/realtime/events")
async def ws_events_legacy(websocket: WebSocket) -> None:
    await _serve_channel(websocket, "events")
