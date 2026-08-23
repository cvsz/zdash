from __future__ import annotations

import logging
from abc import abstractmethod
from typing import Any

from app.ai.base import AIAdapter, AIResponse
from app.ai.mock_adapter import MockAIAdapter
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class OpenAICompatibleAdapter(AIAdapter):
    """Safe boundary for OpenAI-compatible gateway providers.

    Subclasses declare their settings attribute names. When the provider API
    key is missing the adapter degrades to MockAIAdapter (fail-safe, no network).
    The real HTTP integration stays a placeholder until wired, mirroring the
    ClaudeAdapter contract.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @property
    @abstractmethod
    def api_key_setting(self) -> str: ...

    @property
    @abstractmethod
    def base_url_setting(self) -> str: ...

    @property
    @abstractmethod
    def model_setting(self) -> str: ...

    def __init__(self) -> None:
        self.settings = get_settings()
        self._fallback = MockAIAdapter()

    def _should_fallback(self) -> bool:
        return not bool(getattr(self.settings, self.api_key_setting, "").strip())

    def generate_response(
        self, prompt: str, context: dict[str, Any] | None = None
    ) -> AIResponse:
        if self._should_fallback():
            logger.info(
                f"{self.provider_name}_fallback_to_mock",
                extra={"context": {"reason": "missing_api_key"}},
            )
            return self._fallback.generate_response(prompt=prompt, context=context)

        return AIResponse(
            provider=self.provider_name,
            model=getattr(self.settings, self.model_setting),
            text=f"[{self.provider_name.upper()}_PLACEHOLDER] {prompt.strip()}",
            metadata={
                "mode": "placeholder",
                "base_url": getattr(self.settings, self.base_url_setting),
                "fallback_available": True,
            },
        )


class OpenRouterAdapter(OpenAICompatibleAdapter):
    provider_name = "openrouter"
    api_key_setting = "openrouter_api_key"
    base_url_setting = "openrouter_base_url"
    model_setting = "openrouter_model"


class KiloAdapter(OpenAICompatibleAdapter):
    provider_name = "kilo"
    api_key_setting = "kilo_api_key"
    base_url_setting = "kilo_base_url"
    model_setting = "kilo_model"


class OpenCodeAdapter(OpenAICompatibleAdapter):
    provider_name = "opencode"
    api_key_setting = "opencode_api_key"
    base_url_setting = "opencode_base_url"
    model_setting = "opencode_model"
