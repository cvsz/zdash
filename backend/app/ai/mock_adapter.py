from __future__ import annotations

from typing import Any

from app.ai.base import AIAdapter, AIResponse


class MockAIAdapter(AIAdapter):
    def generate_response(
        self, prompt: str, context: dict[str, Any] | None = None
    ) -> AIResponse:
        trimmed = prompt.strip() or "empty prompt"
        suffix = ""
        if context:
            suffix = f" | context_keys={','.join(sorted(context.keys()))}"
        return AIResponse(
            provider="mock",
            model="mock-v1",
            text=f"[MOCK] Janie received: {trimmed}{suffix}",
            metadata={"deterministic": True},
        )
