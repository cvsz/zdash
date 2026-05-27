import asyncio
from unittest.mock import patch

from app.core.events import event_bus
from app.realtime.broadcaster import RealtimeBroadcaster
from app.realtime.events import build_event_envelope
from app.realtime.manager import RealtimeConnectionManager


class FakeWebSocket:
    def __init__(self) -> None:
        self.sent_payloads: list[dict] = []

    async def accept(self) -> None:
        return

    async def send_json(self, payload: dict) -> None:
        self.sent_payloads.append(payload)

    async def close(self, code: int = 1000) -> None:
        return


def test_realtime_broadcaster_buffers_and_delivers_by_channel() -> None:
    async def scenario() -> None:
        manager = RealtimeConnectionManager()
        broadcaster = RealtimeBroadcaster(manager, max_events_per_channel=10)

        websocket = FakeWebSocket()
        await manager.connect("scheduler", websocket)

        envelope = build_event_envelope(
            event_type="scheduler.job.started",
            source="SchedulerService",
            payload={"job_id": "job-1"},
        )
        await broadcaster.apublish(envelope)

        assert websocket.sent_payloads
        assert websocket.sent_payloads[-1]["type"] == "scheduler.started"
        assert broadcaster.recent_events("scheduler", limit=1)[0]["payload"]["job_id"] == "job-1"

    asyncio.run(scenario())


def test_event_bus_emit_invokes_realtime_publish_hook() -> None:
    seen: list[str] = []

    with patch("app.realtime.publish_event") as publish_event:
        publish_event.side_effect = lambda event: seen.append(event.type)
        event_bus.emit(
            event_type="system.connected",
            source="test",
            message="Realtime bridge",
            payload={"ok": True},
        )

    assert "system.connected" in seen
