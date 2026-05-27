import asyncio
import time

from app.realtime.heartbeat import RealtimeHeartbeat
from app.realtime.manager import RealtimeConnectionManager


class FakeWebSocket:
    def __init__(self) -> None:
        self.sent_payloads: list[dict] = []
        self.closed = False

    async def accept(self) -> None:
        return

    async def send_json(self, payload: dict) -> None:
        self.sent_payloads.append(payload)

    async def close(self, code: int = 1000) -> None:
        self.closed = True


def test_heartbeat_sends_ping_and_prunes_stale_connections() -> None:
    async def scenario() -> None:
        manager = RealtimeConnectionManager()
        heartbeat = RealtimeHeartbeat(
            manager,
            ping_interval_seconds=10.0,
            stale_after_seconds=0.5,
        )

        healthy_socket = FakeWebSocket()
        stale_socket = FakeWebSocket()

        healthy_id = await manager.connect("events", healthy_socket)
        stale_id = await manager.connect("events", stale_socket)

        manager.force_last_pong("events", healthy_id, time.time())
        manager.force_last_pong("events", stale_id, time.time() - 2)

        removed = await heartbeat.tick()

        assert removed == 1
        assert manager.snapshot()["events"] == 1
        assert stale_socket.closed is True
        assert healthy_socket.sent_payloads
        assert healthy_socket.sent_payloads[-1]["type"] == "system.ping"

    asyncio.run(scenario())
