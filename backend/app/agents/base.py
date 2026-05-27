from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.core.events import Event, event_bus

AgentStatus = Literal["idle", "running", "error", "disabled"]


class AgentMessage(BaseModel):
    from_agent: str
    to_agent: str
    message: str
    context: dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.id = agent_id
        self.name = name
        self.role = role
        self.status: AgentStatus = "idle"
        self.metadata = metadata or {}

    def emit_event(
        self, event_type: str, message: str, payload: dict[str, Any] | None = None
    ) -> Event:
        return event_bus.emit(
            event_type=event_type,
            source=self.id,
            message=message,
            payload=payload or {},
        )

    @abstractmethod
    def receive_message(self, message: AgentMessage) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def run_task(
        self, task: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        raise NotImplementedError

    def health_check(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "status": self.status,
            "metadata": self.metadata,
        }
