from __future__ import annotations

import asyncio

import httpx
import pytest

from app.integrations.zplatform_voice import (
    VoiceGatewayRejected,
    VoiceIntegrationConfig,
    VoiceIntegrationUnavailable,
    issue_voice_ticket,
)


def _config(**overrides) -> VoiceIntegrationConfig:
    values = {
        "enabled": True,
        "gateway_url": "http://voice-gateway:8450",
        "service_token": "service-token",
        "model": "qwen3:8b",
        "request_timeout_seconds": 5.0,
    }
    values.update(overrides)
    return VoiceIntegrationConfig(**values)


def test_config_fails_closed_when_disabled():
    with pytest.raises(VoiceIntegrationUnavailable, match="disabled"):
        _config(enabled=False).validate()


def test_issue_ticket_propagates_identity_without_exposing_service_token():
    captured: dict[str, object] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["body"] = request.content
        return httpx.Response(
            201,
            json={
                "ticket": "signed-ticket-value-123456",
                "websocket_url": "ws://127.0.0.1:8450/v1/realtime",
                "expires_at": "2030-01-01T00:00:00Z",
                "ticket_transport": "sec-websocket-protocol",
            },
        )

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await issue_voice_ticket(
                tenant_id="tenant-1",
                subject_id="operator@example.com",
                request_id="request-1",
                config=_config(),
                client=client,
            )

    grant = asyncio.run(run())
    headers = captured["headers"]
    assert grant.ticket == "signed-ticket-value-123456"
    assert grant.websocket_url.startswith("ws://")
    assert headers["authorization"] == "Bearer service-token"
    assert headers["x-tenant-id"] == "tenant-1"
    assert headers["x-subject-id"] == "operator@example.com"
    assert headers["x-request-id"] == "request-1"
    assert "service-token" not in grant.model_dump_json()


def test_issue_ticket_rejects_invalid_websocket_contract():
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            201,
            json={
                "ticket": "signed-ticket-value-123456",
                "websocket_url": "https://example.com/not-a-websocket",
                "expires_at": "2030-01-01T00:00:00Z",
                "ticket_transport": "sec-websocket-protocol",
            },
        )

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            await issue_voice_ticket(
                tenant_id="tenant-1",
                subject_id="operator@example.com",
                request_id="request-1",
                config=_config(),
                client=client,
            )

    with pytest.raises(VoiceGatewayRejected, match="invalid response"):
        asyncio.run(run())


def test_gateway_error_message_is_normalized():
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            503,
            json={"error": {"code": "CAPACITY", "message": "Voice capacity reached"}},
        )

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            await issue_voice_ticket(
                tenant_id="tenant-1",
                subject_id="operator@example.com",
                request_id="request-1",
                config=_config(),
                client=client,
            )

    with pytest.raises(VoiceGatewayRejected, match="Voice capacity reached"):
        asyncio.run(run())
