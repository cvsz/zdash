from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from typing import Any

from app.core.config import get_settings


class ImageGenerationAdapter(ABC):
    @abstractmethod
    def generate_image(
        self, prompt: str, options: dict[str, Any] | None = None
    ) -> dict[str, Any]: ...


class MockImageGenerationAdapter(ImageGenerationAdapter):
    def __init__(self, provider_name: str = "mock") -> None:
        self.provider_name = provider_name

    def generate_image(
        self, prompt: str, options: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        normalized_prompt = (prompt or "").strip()
        digest = hashlib.sha1(normalized_prompt.encode()).hexdigest()[:12]
        return {
            "ok": True,
            "dry_run": True,
            "asset_url": f"mock://image/{digest}",
            "provider": self.provider_name,
            "prompt": normalized_prompt,
            "metadata": options or {},
        }


def build_image_adapter(
    *,
    provider: str | None = None,
    dry_run: bool | None = None,
) -> ImageGenerationAdapter:
    settings = get_settings()
    resolved_provider = (provider or settings.image_generation_provider or "mock").lower()
    resolved_dry_run = settings.image_dry_run if dry_run is None else dry_run

    # Phase 06 safety: real image providers are intentionally disabled.
    if resolved_provider != "mock" or not resolved_dry_run:
        return MockImageGenerationAdapter(provider_name=f"mock_fallback:{resolved_provider}")

    return MockImageGenerationAdapter(provider_name=resolved_provider)
