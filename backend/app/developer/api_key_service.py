from __future__ import annotations
import hashlib, hmac, secrets
from datetime import datetime, timedelta, UTC
from fastapi import HTTPException
from app.core.config import get_settings
from app.developer.models import ApiKeyCreateRequest, ApiKeyCreatedResponse, ApiKeyScope, ApiKeyStatus, DeveloperApiKey

_STORE: dict[str, DeveloperApiKey] = {}

class ApiKeyService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _hash(self, raw: str) -> str:
        pepper = self.settings.api_key_hash_pepper
        if self.settings.app_env == "production" and pepper == "change-me-api-key-pepper":
            raise HTTPException(status_code=500, detail="API_KEY_INVALID")
        return hashlib.sha256(f"{pepper}:{raw}".encode()).hexdigest()

    def create_api_key(self, request: ApiKeyCreateRequest, actor_user_id: str, tenant_context: dict) -> ApiKeyCreatedResponse:
        key_id = secrets.token_hex(8)
        mode = "sandbox" if request.sandbox_only else "live"
        raw = f"{self.settings.api_key_prefix}_{mode}_{secrets.token_urlsafe(24)}"
        now = datetime.now(UTC)
        model = DeveloperApiKey(
            id=key_id, organization_id=tenant_context["organization_id"], workspace_id=tenant_context["workspace_id"],
            name=request.name, prefix="_".join(raw.split("_")[:2]), key_hash=self._hash(raw), scopes=request.scopes,
            status=ApiKeyStatus.ACTIVE, expires_at=request.expires_at or now + timedelta(days=self.settings.api_key_default_expires_days),
            created_by=actor_user_id, created_at=now, updated_at=now, sandbox_only=request.sandbox_only,
        )
        _STORE[key_id] = model
        return ApiKeyCreatedResponse(id=key_id, name=request.name, raw_key=raw, prefix=model.prefix, scopes=model.scopes, expires_at=model.expires_at)

    def list_api_keys(self, tenant_context: dict) -> list[DeveloperApiKey]:
        return [k for k in _STORE.values() if k.organization_id == tenant_context["organization_id"] and k.workspace_id == tenant_context["workspace_id"]]

    def authenticate_raw_key(self, raw_key: str) -> DeveloperApiKey | None:
        digest = self._hash(raw_key)
        now = datetime.now(UTC)
        for key in _STORE.values():
            if hmac.compare_digest(key.key_hash, digest):
                if key.status in {ApiKeyStatus.DISABLED, ApiKeyStatus.REVOKED}: return None
                if key.expires_at and key.expires_at < now: return None
                return key
        return None

    def verify_scope(self, api_key: DeveloperApiKey, required_scope: ApiKeyScope) -> bool:
        return required_scope in api_key.scopes or ApiKeyScope.SANDBOX_ALL in api_key.scopes

service = ApiKeyService()
