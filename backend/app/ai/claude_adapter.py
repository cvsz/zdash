from __future__ import annotations

import logging
from typing import Any

from app.ai.base import AIAdapter, AIResponse
from app.ai.mock_adapter import MockAIAdapter
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ClaudeAdapter(AIAdapter):
    """
    Safe Claude adapter boundary.

    If CLAUDE_API_KEY is missing or Claude SDK integration is unavailable,
    this adapter falls back to MockAIAdapter.

    Production integration point:
    - install Anthropic SDK
    - replace fallback branch with real API call
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self._fallback = MockAIAdapter()

    def _should_fallback(self) -> bool:
        if not self.settings.claude_api_key:
            return True
        return False

    def generate_response(
        self, prompt: str, context: dict[str, Any] | None = None
    ) -> AIResponse:
        if self._should_fallback():
            logger.info(
                "claude_fallback_to_mock",
                extra={"context": {"reason": "missing_key_or_sdk"}},
            )
            return self._fallback.generate_response(prompt=prompt, context=context)

        # Placeholder for real Claude integration.
        # Keep safe fallback if SDK path is not wired yet.
        return AIResponse(
            provider="claude",
            model=self.settings.claude_model,
            text=f"[CLAUDE_PLACEHOLDER] {prompt.strip()}",
            metadata={"mode": "placeholder", "fallback_available": True},
        )
