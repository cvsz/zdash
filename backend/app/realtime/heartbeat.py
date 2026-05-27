from __future__ import annotations

import asyncio
from contextlib import suppress

from app.realtime.events import CHANNELS
from app.realtime.manager import RealtimeConnectionManager, get_realtime_connection_manager
from app.realtime.schemas import RealtimeEventEnvelope


class RealtimeHeartbeat:
    def __init__(
        self,
        manager: RealtimeConnectionManager,
        *,
        ping_interval_seconds: float = 15.0,
        stale_after_seconds: float = 45.0,
    ) -> None:
        self._manager = manager
        self._ping_interval_seconds = ping_interval_seconds
        self._stale_after_seconds = stale_after_seconds
        self._task: asyncio.Task[None] | None = None

    def start(self) -> None:
        if self._task is not None and not self._task.done():
            return
        self._task = asyncio.create_task(self._run(), name="realtime-heartbeat")

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        with suppress(asyncio.CancelledError):
            await self._task
        self._task = None

    async def tick(self) -> int:
        ping = RealtimeEventEnvelope(
            type="system.ping",
            source="realtime.heartbeat",
            severity="info",
            payload={"heartbeat": True},
        ).model_dump(mode="json")
        await self._manager.broadcast_channels(set(CHANNELS), ping)
        return await self._manager.prune_stale(self._stale_after_seconds)

    async def _run(self) -> None:
        while True:
            await asyncio.sleep(self._ping_interval_seconds)
            await self.tick()


_heartbeat: RealtimeHeartbeat | None = None


def get_realtime_heartbeat() -> RealtimeHeartbeat:
    global _heartbeat
    if _heartbeat is None:
        _heartbeat = RealtimeHeartbeat(get_realtime_connection_manager())
    return _heartbeat


async def stop_realtime_heartbeat() -> None:
    global _heartbeat
    if _heartbeat is None:
        return
    await _heartbeat.stop()
    _heartbeat = None
