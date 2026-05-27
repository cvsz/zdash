from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from typing import Any

from app.content.models import ContentPlatform, SocialPostResult
from app.core.config import Settings, get_settings


class SocialMediaAdapter(ABC):
    @abstractmethod
    def publish(
        self,
        platform: ContentPlatform,
        text: str,
        asset_url: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> SocialPostResult: ...


class MockSocialMediaAdapter(SocialMediaAdapter):
    def publish(
        self,
        platform: ContentPlatform,
        text: str,
        asset_url: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> SocialPostResult:
        key = f"{platform.value}:{text}:{asset_url}:{metadata or {}}"
        external_id = hashlib.sha1(key.encode()).hexdigest()[:12]
        return SocialPostResult(
            platform=platform,
            ok=True,
            dry_run=True,
            external_id=f"mock-{external_id}",
            message="Simulated publish",
            output=metadata or {},
        )


class _CredentialGuardedStubAdapter(SocialMediaAdapter):
    def __init__(self, platform_name: str, token: str = "") -> None:
        self.platform_name = platform_name
        self.token = token

    def publish(
        self,
        platform: ContentPlatform,
        text: str,
        asset_url: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> SocialPostResult:
        token_available = bool((self.token or "").strip())
        if not token_available:
            message = f"{self.platform_name} token missing"
            output = {"blocked": True, "reason": "missing_credentials"}
        else:
            message = f"{self.platform_name} adapter is stub-only in phase 06"
            output = {"blocked": True, "reason": "provider_stub_not_implemented"}
        return SocialPostResult(
            platform=platform,
            ok=False,
            dry_run=False,
            external_id=None,
            message=message,
            output=output | (metadata or {}),
        )


class XAdapter(_CredentialGuardedStubAdapter):
    def __init__(self, token: str = "") -> None:
        super().__init__("x", token)


class TikTokAdapter(_CredentialGuardedStubAdapter):
    def __init__(self, token: str = "") -> None:
        super().__init__("tiktok", token)


class FacebookAdapter(_CredentialGuardedStubAdapter):
    def __init__(self, token: str = "") -> None:
        super().__init__("facebook", token)


class InstagramAdapter(_CredentialGuardedStubAdapter):
    def __init__(self, token: str = "") -> None:
        super().__init__("instagram", token)


class LinkedInAdapter(_CredentialGuardedStubAdapter):
    def __init__(self, token: str = "") -> None:
        super().__init__("linkedin", token)


def build_platform_adapters(
    settings: Settings | None = None,
) -> dict[ContentPlatform, SocialMediaAdapter]:
    cfg = settings or get_settings()
    return {
        ContentPlatform.x: XAdapter(token=cfg.social_x_api_key),
        ContentPlatform.tiktok: TikTokAdapter(token=cfg.social_tiktok_access_token),
        ContentPlatform.facebook: FacebookAdapter(token=cfg.social_facebook_access_token),
        ContentPlatform.instagram: InstagramAdapter(
            token=cfg.social_instagram_access_token
        ),
        ContentPlatform.linkedin: LinkedInAdapter(
            token=cfg.social_linkedin_access_token
        ),
        ContentPlatform.blog: MockSocialMediaAdapter(),
        ContentPlatform.generic: MockSocialMediaAdapter(),
    }
