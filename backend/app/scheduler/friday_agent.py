from __future__ import annotations

from app.agents.friday import FridayAgent

_friday_agent: FridayAgent | None = None


def get_friday_agent() -> FridayAgent:
    global _friday_agent
    if _friday_agent is None:
        _friday_agent = FridayAgent()
    return _friday_agent


def reset_friday_agent() -> None:
    global _friday_agent
    _friday_agent = None


friday_agent = get_friday_agent()
