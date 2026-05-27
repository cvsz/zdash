from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod

from app.content.models import ContentPlatform, SocialPostResult


class SocialMediaAdapter(ABC):
    @abstractmethod
    def publish(
        self,
        platform: ContentPlatform,
        text: str,
        asset_url: str | None,
        metadata: dict | None = None,
    ) -> SocialPostResult: ...


class MockSocialMediaAdapter(SocialMediaAdapter):
    def publish(
        self,
        platform: ContentPlatform,
        text: str,
        asset_url: str | None,
        metadata: dict | None = None,
    ) -> SocialPostResult:
        key = f"{platform.value}:{text}:{asset_url}"
        external_id = hashlib.md5(key.encode()).hexdigest()[:10]
        return SocialPostResult(
            platform=platform,
            ok=True,
            dry_run=True,
            external_id=f"mock-{external_id}",
            message="Simulated publish",
            output=metadata or {},
        )


class _StubPlatformAdapter(SocialMediaAdapter):
    def publish(
        self,
        platform: ContentPlatform,
        text: str,
        asset_url: str | None,
        metadata: dict | None = None,
    ) -> SocialPostResult:
        return SocialPostResult(
            platform=platform,
            ok=False,
            dry_run=False,
            external_id=None,
            message="Missing credentials or provider stub.",
            output={"blocked": True},
        )


XAdapter = TikTokAdapter = FacebookAdapter = InstagramAdapter = LinkedInAdapter = (
    _StubPlatformAdapter
)
