from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class AIResponse(BaseModel):
    provider: str
    model: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIAdapter(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, context: dict[str, Any] | None = None) -> AIResponse:
        raise NotImplementedError
