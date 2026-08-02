from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator

from app.auth.dependencies import get_current_user
from app.auth.models import AuthSession
from app.core.config import get_settings
from app.core.events import event_bus
from app.core.responses import ok
from app.integrations.zplatform_voice import (
    VoiceGatewayRejected,
    VoiceIntegrationConfig,
    VoiceIntegrationUnavailable,
    issue_voice_ticket,
)

router = APIRouter(prefix="/api/voice", tags=["voice"])


class VoiceSessionRequest(BaseModel):
    instructions: str = Field(
        default="You are a concise, helpful voice assistant. Reply in the user's language.",
        min_length=1,
        max_length=8000,
    )

    @field_validator("instructions")
    @classmethod
    def validate_instructions(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Voice instructions must not be blank")
        return normalized


def _tenant_id(request: Request) -> str:
    settings = get_settings()
    value = request.headers.get(settings.tenant_header_name, "").strip()
    return value or "default"


@router.get("/status")
def voice_status(current_user: AuthSession = Depends(get_current_user)):
    config = VoiceIntegrationConfig.from_env()
    configured = bool(config.gateway_url and config.service_token)
    return ok(
        {
            "enabled": config.enabled,
            "configured": configured,
            "model": config.model,
            "subject": current_user.username,
        }
    )


@router.post("/session")
async def create_voice_session(
    payload: VoiceSessionRequest,
    request: Request,
    current_user: AuthSession = Depends(get_current_user),
):
    request_id = request.headers.get("X-Request-Id", "").strip() or str(uuid4())
    tenant_id = _tenant_id(request)
    config = VoiceIntegrationConfig.from_env()

    try:
        grant = await issue_voice_ticket(
            tenant_id=tenant_id,
            subject_id=current_user.username,
            request_id=request_id,
            config=config,
        )
    except VoiceIntegrationUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except VoiceGatewayRejected as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    event_bus.emit(
        "voice.session.issued",
        "app.api.voice",
        "z-platform voice session ticket issued",
        {
            "tenant_id": tenant_id,
            "subject": current_user.username,
            "role": current_user.role,
            "request_id": request_id,
            "model": config.model,
            "expires_at": grant.expires_at.isoformat(),
        },
    )

    return ok(
        {
            "ticket": grant.ticket,
            "websocket_url": grant.websocket_url,
            "expires_at": grant.expires_at.isoformat(),
            "ticket_transport": grant.ticket_transport,
            "model": config.model,
            "instructions": payload.instructions,
        }
    )
