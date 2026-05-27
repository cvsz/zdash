from fastapi import APIRouter, WebSocket
from app.realtime.websocket_manager import manager
from app.realtime.event_stream import recent

router = APIRouter(prefix="/api/realtime", tags=["realtime"])


@router.websocket("/events")
async def ws_events(ws: WebSocket):
    await manager.connect(ws)
    try:
        for e in recent():
            await ws.send_json(e)
        while True:
            await ws.receive_text()
            await ws.send_json({"type": "heartbeat"})
    except Exception:
        manager.disconnect(ws)
