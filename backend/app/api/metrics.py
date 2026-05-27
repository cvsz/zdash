from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import decode_token
from app.core.config import get_settings
from app.observability.metrics import render_metrics

router = APIRouter(prefix="/api", tags=["metrics"])
bearer_scheme = HTTPBearer(auto_error=False)


def _require_metrics_access(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    settings = get_settings()
    if not settings.metrics_auth_required:
        return
    if not settings.is_production and settings.metrics_allow_unauthenticated_dev:
        return
    if not settings.auth_enabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Metrics requires authenticated admin access",
        )
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    try:
        payload = decode_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
        ) from exc
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    if str(payload.get("role", "viewer")) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )


@router.get("/metrics", response_class=PlainTextResponse)
def metrics(_: None = Depends(_require_metrics_access)):
    return render_metrics()
