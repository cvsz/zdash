import asyncio

from app.realtime.manager import RealtimeConnectionManager


class FakeWebSocket:
    def __init__(self, *, fail_on_send: bool = False) -> None:
        self.accepted = False
        self.closed = False
        self.close_code: int | None = None
        self.sent_payloads: list[dict] = []
        self._fail_on_send = fail_on_send

    async def accept(self) -> None:
        self.accepted = True

    async def send_json(self, payload: dict) -> None:
        if self._fail_on_send:
            raise RuntimeError("send failure")
        self.sent_payloads.append(payload)

    async def close(self, code: int = 1000) -> None:
        self.closed = True
        self.close_code = code


def test_manager_tracks_connections_and_broadcasts() -> None:
    async def scenario() -> None:
        manager = RealtimeConnectionManager()
        websocket = FakeWebSocket()

        client_id = await manager.connect("events", websocket)  # type: ignore[arg-type]
        assert websocket.accepted is True
        assert manager.snapshot()["events"] == 1

        delivered = await manager.broadcast("events", {"type": "system.connected"})
        assert delivered == 1
        assert websocket.sent_payloads[-1]["type"] == "system.connected"

        await manager.disconnect("events", client_id, close_code=1000)  # type: ignore[arg-type]
        assert manager.snapshot()["events"] == 0
        assert websocket.closed is True

    asyncio.run(scenario())


def test_manager_cleans_up_dead_connections_on_broadcast() -> None:
    async def scenario() -> None:
        manager = RealtimeConnectionManager()
        websocket = FakeWebSocket(fail_on_send=True)
        await manager.connect("risk", websocket)  # type: ignore[arg-type]

        delivered = await manager.broadcast("risk", {"type": "risk.alert"})  # type: ignore[arg-type]
        assert delivered == 0
        assert manager.snapshot()["risk"] == 0
        assert websocket.closed is True
        assert websocket.close_code == 1011

    asyncio.run(scenario())
