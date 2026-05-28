"""Phase 33 AI Trader simulation layer.

The AI trader package is simulation-only. It generates deterministic TradingSignal
objects and delegates validation/execution to the existing zDash trading stack.
"""

from app.ai_trader.service import AITraderService

__all__ = ["AITraderService"]
