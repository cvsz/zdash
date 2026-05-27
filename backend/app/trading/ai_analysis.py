from __future__ import annotations

from app.ai.base import AIAdapter
from app.ai.claude_adapter import ClaudeAdapter
from app.ai.mock_adapter import MockAIAdapter
from app.core.config import get_settings
from app.trading.models import Candle, TradingSignal


class TradingAIAnalysis:
    def __init__(self, adapter: AIAdapter | None = None) -> None:
        self.settings = get_settings()
        self.adapter = adapter or self._build_adapter()

    def _build_adapter(self) -> AIAdapter:
        if self.settings.ai_trading_provider.lower() == "claude":
            return ClaudeAdapter()
        return MockAIAdapter()

    @staticmethod
    def _disclaimer() -> str:
        return "Simulation only. Not financial advice. No live execution."

    def summarize_signal(self, signal: TradingSignal, context: dict | None = None) -> str:
        if not self.settings.ai_trading_analysis_enabled:
            return f"{self._disclaimer()} AI analysis is disabled."

        prompt = (
            f"Summarize a dry-run trading signal for {signal.symbol} {signal.timeframe}. "
            f"Direction={signal.direction}, confidence={signal.confidence:.2f}, "
            f"entry={signal.entry}, stop={signal.stop_loss}, target={signal.take_profit}."
        )
        ai_response = self.adapter.generate_response(prompt=prompt, context=context or {})
        return f"{ai_response.text} | {self._disclaimer()}"

    def analyze_scanner_context(self, candles: list[Candle], signal: TradingSignal) -> str:
        candle_count = len(candles)
        recent_close = candles[-1].close if candles else 0.0
        context = {
            "candles": candle_count,
            "recent_close": recent_close,
            "provider": self.settings.ai_trading_provider,
        }
        return self.summarize_signal(signal=signal, context=context)
