from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import decode_token
from app.auth.models import AuthSession
from app.auth.rbac import Permission, has_permission
from app.core.config import get_settings

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthSession:
    settings = get_settings()
    if not settings.auth_enabled:
        return AuthSession(username="dev-user", role="admin")

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
    username = str(payload.get("sub", "")).strip()
    role = str(payload.get("role", "viewer")).strip() or "viewer"
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )
    return AuthSession(username=username, role=role)


def require_authenticated(user: AuthSession = Depends(get_current_user)) -> AuthSession:
    return user


def require_permission(permission: Permission):
    def _dependency(user: AuthSession = Depends(get_current_user)) -> AuthSession:
        if not has_permission(user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return _dependency


def require_permissions(permissions: list[Permission]):
    """Dependency factory: user must have ALL listed permissions (or be admin)."""

    def _dependency(user: AuthSession = Depends(get_current_user)) -> AuthSession:
        for perm in permissions:
            if not has_permission(user.role, perm):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
        return user

    return _dependency
