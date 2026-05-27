from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod


class ImageGenerationAdapter(ABC):
    @abstractmethod
    def generate_image(self, prompt: str, options: dict | None = None) -> dict: ...


class MockImageGenerationAdapter(ImageGenerationAdapter):
    def generate_image(self, prompt: str, options: dict | None = None) -> dict:
        digest = hashlib.sha1(prompt.encode()).hexdigest()[:12]
        return {
            "ok": True,
            "dry_run": True,
            "asset_url": f"mock://image/{digest}",
            "provider": "mock",
            "prompt": prompt,
            "metadata": options or {},
        }
