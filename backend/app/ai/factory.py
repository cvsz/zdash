from __future__ import annotations

from app.ai.base import AIAdapter
from app.ai.claude_adapter import ClaudeAdapter
from app.ai.mock_adapter import MockAIAdapter
from app.ai.openai_compat_adapter import (
    KiloAdapter,
    OpenCodeAdapter,
    OpenRouterAdapter,
)
from app.core.config import get_settings

_ADAPTERS: dict[str, type[AIAdapter]] = {
    "claude": ClaudeAdapter,
    "openrouter": OpenRouterAdapter,
    "kilo": KiloAdapter,
    "opencode": OpenCodeAdapter,
}

KNOWN_PROVIDERS = sorted({"mock", *_ADAPTERS})


def build_adapter(provider: str | None = None) -> AIAdapter:
    """Resolve a provider name to its adapter; unknown/empty names fall back to mock."""
    name = (provider or get_settings().ai_provider).strip().lower()
    adapter_cls = _ADAPTERS.get(name)
    if adapter_cls is None:
        return MockAIAdapter()
    return adapter_cls()
