from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel, ConfigDict, Field, field_validator


class VoiceIntegrationError(RuntimeError):
    """Base error for the z-platform voice integration."""


class VoiceIntegrationUnavailable(VoiceIntegrationError):
    """Raised when the integration is disabled or incomplete."""


class VoiceGatewayRejected(VoiceIntegrationError):
    """Raised when the trusted voice gateway rejects a ticket request."""


def _environment_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return -1


@dataclass(frozen=True)
class VoiceIntegrationConfig:
    enabled: bool
    gateway_url: str
    service_token: str
    model: str
    request_timeout_seconds: float

    @classmethod
    def from_env(cls) -> VoiceIntegrationConfig:
        return cls(
            enabled=os.getenv("ZPLATFORM_VOICE_ENABLED", "false").strip().lower()
            == "true",
            gateway_url=os.getenv("ZPLATFORM_VOICE_GATEWAY_URL", "")
            .strip()
            .rstrip("/"),
            service_token=os.getenv("ZPLATFORM_VOICE_SERVICE_TOKEN", "").strip(),
            model=os.getenv("ZPLATFORM_VOICE_MODEL", "qwen3:8b").strip() or "qwen3:8b",
            request_timeout_seconds=_environment_float(
                "ZPLATFORM_VOICE_REQUEST_TIMEOUT_SECONDS", 5.0
            ),
        )

    def validate(self) -> None:
        if not self.enabled:
            raise VoiceIntegrationUnavailable("Voice integration is disabled")
        if not self.gateway_url or not self.service_token:
            raise VoiceIntegrationUnavailable(
                "Voice integration is missing gateway credentials"
            )
        parsed = urlparse(self.gateway_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise VoiceIntegrationUnavailable("Voice gateway URL is invalid")
        if not 0.5 <= self.request_timeout_seconds <= 30:
            raise VoiceIntegrationUnavailable("Voice request timeout is invalid")


class VoiceGatewayGrant(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ticket: str = Field(min_length=16, max_length=4096)
    websocket_url: str = Field(min_length=8, max_length=2048)
    expires_at: datetime
    ticket_transport: str = Field(default="sec-websocket-protocol")

    @field_validator("websocket_url")
    @classmethod
    def validate_websocket_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"ws", "wss"} or not parsed.netloc:
            raise ValueError("Voice gateway returned an invalid WebSocket URL")
        return value

    @field_validator("ticket_transport")
    @classmethod
    def validate_transport(cls, value: str) -> str:
        if value != "sec-websocket-protocol":
            raise ValueError("Unsupported voice ticket transport")
        return value


async def issue_voice_ticket(
    *,
    tenant_id: str,
    subject_id: str,
    request_id: str,
    config: VoiceIntegrationConfig | None = None,
    client: httpx.AsyncClient | None = None,
) -> VoiceGatewayGrant:
    resolved = config or VoiceIntegrationConfig.from_env()
    resolved.validate()

    tenant = tenant_id.strip() or "default"
    subject = subject_id.strip()
    if not subject:
        raise VoiceIntegrationUnavailable("Voice session subject is missing")

    owns_client = client is None
    http_client = client or httpx.AsyncClient(
        timeout=httpx.Timeout(resolved.request_timeout_seconds),
        follow_redirects=False,
    )
    try:
        response = await http_client.post(
            f"{resolved.gateway_url}/v1/voice/tickets",
            headers={
                "Authorization": f"Bearer {resolved.service_token}",
                "Content-Type": "application/json",
                "X-Tenant-Id": tenant,
                "X-Subject-Id": subject,
                "X-Request-Id": request_id,
            },
            json={"model": resolved.model},
        )
    except httpx.TimeoutException as exc:
        raise VoiceGatewayRejected("Voice gateway request timed out") from exc
    except httpx.HTTPError as exc:
        raise VoiceGatewayRejected("Voice gateway is unavailable") from exc
    finally:
        if owns_client:
            await http_client.aclose()

    if response.status_code != 201:
        message = "Voice gateway rejected the session request"
        try:
            payload = response.json()
            candidate = payload.get("error") if isinstance(payload, dict) else None
            if isinstance(candidate, dict) and isinstance(
                candidate.get("message"), str
            ):
                message = candidate["message"]
        except ValueError:
            pass
        raise VoiceGatewayRejected(message)

    try:
        return VoiceGatewayGrant.model_validate(response.json())
    except (ValueError, TypeError) as exc:
        raise VoiceGatewayRejected(
            "Voice gateway returned an invalid response"
        ) from exc
