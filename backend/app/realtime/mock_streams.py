from __future__ import annotations

import asyncio
import os
from itertools import cycle

from app.realtime.broadcaster import get_realtime_broadcaster
from app.realtime.events import build_event_envelope

_EVENTS = cycle([
    ("risk.drawdown.warning", "risk", "warning", "guardian", "Drawdown warning threshold reached"),
    ("scheduler.job.tick", "scheduler", "info", "scheduler", "Scheduled heartbeat job completed"),
    ("content.pipeline.updated", "content", "info", "content", "Draft queued for approval"),
    ("trading.signal.generated", "trading", "info", "scanner", "Dry-run signal generated"),
    ("system.health.warning", "system", "warning", "health", "System latency elevated"),
])

_task: asyncio.Task[None] | None = None


async def _run() -> None:
    broadcaster = get_realtime_broadcaster()
    while True:
        ev_type, category, severity, source, message = next(_EVENTS)
        await broadcaster.apublish(
            build_event_envelope(
                event_type=ev_type,
                source=source,
                severity=severity,  # type: ignore[arg-type]
                message=message,
                payload={"category": category, "dry_run": True},
            )
        )
        await asyncio.sleep(3)


def start_mock_stream_if_enabled() -> None:
    global _task
    enabled = os.getenv("ENABLE_MOCK_REALTIME", "false").lower() == "true"
    is_pytest = os.getenv("PYTEST_CURRENT_TEST") is not None
    if not enabled or is_pytest or _task is not None:
        return
    _task = asyncio.create_task(_run())


async def stop_mock_stream() -> None:
    global _task
    if _task is None:
        return
    _task.cancel()
    try:
        await _task
    except asyncio.CancelledError:
        pass
    _task = None
