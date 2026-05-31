from __future__ import annotations

import asyncio
import time
from contextlib import suppress
from dataclasses import dataclass
from uuid import uuid4

from fastapi import WebSocket

from app.realtime.events import CHANNELS
from app.realtime.schemas import RealtimeChannel


@dataclass
class ManagedConnection:
    client_id: str
    channel: RealtimeChannel
    websocket: WebSocket
    connected_at: float
    last_seen_at: float
    last_pong_at: float


class RealtimeConnectionManager:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._connections: dict[RealtimeChannel, dict[str, ManagedConnection]] = {
            channel: {} for channel in CHANNELS
        }

    async def connect(self, channel: RealtimeChannel, websocket: WebSocket) -> str:
        await websocket.accept()
        now = time.time()
        client_id = str(uuid4())
        connection = ManagedConnection(
            client_id=client_id,
            channel=channel,
            websocket=websocket,
            connected_at=now,
            last_seen_at=now,
            last_pong_at=now,
        )
        async with self._lock:
            self._connections[channel][client_id] = connection
        return client_id

    async def disconnect(
        self, channel: RealtimeChannel, client_id: str, close_code: int | None = None
    ) -> None:
        connection: ManagedConnection | None = None
        async with self._lock:
            connection = self._connections[channel].pop(client_id, None)

        if connection and close_code is not None:
            with suppress(Exception):
                await connection.websocket.close(code=close_code)

    async def mark_activity(self, channel: RealtimeChannel, client_id: str) -> None:
        async with self._lock:
            connection = self._connections[channel].get(client_id)
            if connection:
                connection.last_seen_at = time.time()

    async def mark_pong(self, channel: RealtimeChannel, client_id: str) -> None:
        now = time.time()
        async with self._lock:
            connection = self._connections[channel].get(client_id)
            if connection:
                connection.last_seen_at = now
                connection.last_pong_at = now

    async def broadcast(self, channel: RealtimeChannel, payload: dict) -> int:
        async with self._lock:
            clients = list(self._connections[channel].items())

        delivered = 0
        stale_ids: list[str] = []

        for client_id, connection in clients:
            try:
                await connection.websocket.send_json(payload)
                delivered += 1
                await self.mark_activity(channel, client_id)
            except Exception:
                stale_ids.append(client_id)

        for stale_id in stale_ids:
            await self.disconnect(channel, stale_id, close_code=1011)

        return delivered

    async def broadcast_channels(
        self, channels: list[RealtimeChannel] | set[RealtimeChannel], payload: dict
    ) -> dict[RealtimeChannel, int]:
        results: dict[RealtimeChannel, int] = {}
        for channel in channels:
            results[channel] = await self.broadcast(channel, payload)
        return results

    async def prune_stale(self, stale_after_seconds: float) -> int:
        now = time.time()
        stale_refs: list[tuple[RealtimeChannel, str]] = []

        async with self._lock:
            for channel, channel_connections in self._connections.items():
                for client_id, connection in channel_connections.items():
                    elapsed = now - connection.last_pong_at
                    if elapsed > stale_after_seconds:
                        stale_refs.append((channel, client_id))

        for channel, client_id in stale_refs:
            await self.disconnect(channel, client_id, close_code=1011)

        return len(stale_refs)

    def snapshot(self) -> dict[str, int]:
        counts: dict[str, int] = {channel: len(connections) for channel, connections in self._connections.items()}
        counts["total"] = sum(counts.values())
        return counts

    def force_last_pong(self, channel: RealtimeChannel, client_id: str, epoch_seconds: float) -> None:
        connection = self._connections.get(channel, {}).get(client_id)
        if connection is not None:
            connection.last_pong_at = epoch_seconds


_connection_manager: RealtimeConnectionManager | None = None


def get_realtime_connection_manager() -> RealtimeConnectionManager:
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = RealtimeConnectionManager()
    return _connection_manager


def reset_realtime_connection_manager() -> None:
    global _connection_manager
    _connection_manager = None
