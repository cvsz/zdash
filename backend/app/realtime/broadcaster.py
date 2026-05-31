from __future__ import annotations

import asyncio
from collections import deque
from threading import Lock
from typing import Any

from app.realtime.events import CHANNELS, channels_for_event, envelope_from_core_event
from app.realtime.manager import (
    RealtimeConnectionManager,
    get_realtime_connection_manager,
)
from app.realtime.schemas import (
    RealtimeChannel,
    RealtimeEventEnvelope,
    RealtimeSeverity,
)


class RealtimeBroadcaster:
    def __init__(
        self,
        manager: RealtimeConnectionManager,
        *,
        max_events_per_channel: int = 500,
    ) -> None:
        self._manager = manager
        self._loop: asyncio.AbstractEventLoop | None = None
        self._lock = Lock()
        self._buffers: dict[RealtimeChannel, deque[dict[str, Any]]] = {
            channel: deque(maxlen=max_events_per_channel) for channel in CHANNELS
        }

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def recent_events(self, channel: RealtimeChannel, limit: int = 100) -> list[dict[str, Any]]:
        safe_limit = max(1, min(limit, 500))
        with self._lock:
            data = list(self._buffers[channel])
        return data[-safe_limit:]

    def publish(
        self,
        envelope: RealtimeEventEnvelope,
        *,
        channels: list[RealtimeChannel] | set[RealtimeChannel] | None = None,
    ) -> dict[str, Any]:
        payload = envelope.model_dump(mode="json")
        targets = set(channels or channels_for_event(envelope.type))

        with self._lock:
            for channel in targets:
                self._buffers[channel].append(payload)

        loop = self._loop
        if loop is not None and loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                self._manager.broadcast_channels(targets, payload), loop
            )
            future.add_done_callback(self._consume_future_exception)  # type: ignore[arg-type]

        return payload

    async def apublish(
        self,
        envelope: RealtimeEventEnvelope,
        *,
        channels: list[RealtimeChannel] | set[RealtimeChannel] | None = None,
    ) -> dict[str, Any]:
        payload = envelope.model_dump(mode="json")
        targets = set(channels or channels_for_event(envelope.type))

        with self._lock:
            for channel in targets:
                self._buffers[channel].append(payload)

        await self._manager.broadcast_channels(targets, payload)
        return payload

    def publish_core_event(self, event: Any) -> dict[str, Any]:
        envelope = envelope_from_core_event(event)
        return self.publish(envelope)

    def connection_snapshot(self) -> dict[str, int]:
        return self._manager.snapshot()

    @staticmethod
    def _consume_future_exception(future: asyncio.Future[Any]) -> None:
        try:
            future.result()
        except Exception:
            # Background websocket broadcast failures are handled by the manager.
            return


_broadcaster: RealtimeBroadcaster | None = None


def get_realtime_broadcaster() -> RealtimeBroadcaster:
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = RealtimeBroadcaster(get_realtime_connection_manager())
    return _broadcaster


def reset_realtime_broadcaster() -> None:
    global _broadcaster
    _broadcaster = None


def bind_realtime_loop(loop: asyncio.AbstractEventLoop) -> None:
    get_realtime_broadcaster().bind_loop(loop)


def publish_event(event: Any) -> dict[str, Any]:
    return get_realtime_broadcaster().publish_core_event(event)


def broadcast_risk_alert(payload: dict[str, Any], source: str = "guardian") -> dict[str, Any]:
    envelope = RealtimeEventEnvelope(
        type="risk.alert",
        source=source,
        severity="warning",
        payload=payload,
    )
    return get_realtime_broadcaster().publish(envelope, channels={"events", "risk"})


def broadcast_scheduler_run(payload: dict[str, Any], source: str = "scheduler") -> dict[str, Any]:
    envelope = RealtimeEventEnvelope(
        type="scheduler.started",
        source=source,
        severity="info",
        payload=payload,
    )
    return get_realtime_broadcaster().publish(
        envelope, channels={"events", "scheduler"}
    )


def broadcast_content_update(payload: dict[str, Any], source: str = "content") -> dict[str, Any]:
    envelope = RealtimeEventEnvelope(
        type="content.created",
        source=source,
        severity="info",
        payload=payload,
    )
    return get_realtime_broadcaster().publish(envelope, channels={"events", "content"})


def broadcast_system_status(
    event_type: str,
    payload: dict[str, Any],
    *,
    source: str = "realtime",
    severity: RealtimeSeverity = "info",
    channels: list[RealtimeChannel] | set[RealtimeChannel] | None = None,
) -> dict[str, Any]:
    envelope = RealtimeEventEnvelope(
        type=event_type,
        source=source,
        severity=severity,
        payload=payload,
    )
    return get_realtime_broadcaster().publish(
        envelope,
        channels=channels or {"events"},
    )
