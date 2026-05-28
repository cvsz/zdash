from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.risk.models import AccountSnapshot
from app.trading.models import Candle, ExecutionRequest, ExecutionResult, SignalValidationResult, TradingSignal
from app.trading.trading_service import TradingService

MODEL_VERSION = "phase33-deterministic-ai-trader-v1"
SAFETY_NOTICE = (
    "Simulation only. Not financial advice. No live execution. "
    "All execution is forced through zDash dry-run trading safety controls."
)


@dataclass(frozen=True)
class FeatureSummary:
    close: float
    fast_ma: float
    slow_ma: float
    momentum_3: float
    atr_proxy: float
    volatility_percent: float
    candles_analyzed: int

    def as_dict(self) -> dict[str, float | int]:
        return {
            "close": self.close,
            "fast_ma": self.fast_ma,
            "slow_ma": self.slow_ma,
            "momentum_3": self.momentum_3,
            "atr_proxy": self.atr_proxy,
            "volatility_percent": self.volatility_percent,
            "candles_analyzed": self.candles_analyzed,
        }


class AITraderService:
    """Deterministic, simulation-only AI trader signal generator.

    This service does not execute orders directly. It produces TradingSignal objects
    and routes validation/execution through the existing TradingService stack.
    """

    def __init__(self, trading_service: TradingService | None = None) -> None:
        self.trading_service = trading_service or TradingService()
        self.model_version = MODEL_VERSION

    @staticmethod
    def _mean(values: list[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    @staticmethod
    def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
        return max(low, min(high, value))

    @staticmethod
    def _true_range_proxy(candle: Candle) -> float:
        return max(candle.high - candle.low, abs(candle.close - candle.open), 0.0)

    def compute_features(
        self,
        candles: list[Candle],
        fast_window: int = 7,
        slow_window: int = 21,
    ) -> FeatureSummary | None:
        if len(candles) < slow_window:
            return None

        ordered = sorted(candles, key=lambda item: item.timestamp)
        closes = [c.close for c in ordered]
        latest = ordered[-1]
        fast_ma = self._mean(closes[-fast_window:])
        slow_ma = self._mean(closes[-slow_window:])
        momentum_3 = latest.close - closes[-4] if len(closes) >= 4 else 0.0
        ranges = [self._true_range_proxy(candle) for candle in ordered[-slow_window:]]
        atr_proxy = max(self._mean(ranges), latest.close * 0.0005, 0.01)
        volatility_percent = (atr_proxy / latest.close) * 100 if latest.close else 0.0

        return FeatureSummary(
            close=latest.close,
            fast_ma=fast_ma,
            slow_ma=slow_ma,
            momentum_3=momentum_3,
            atr_proxy=atr_proxy,
            volatility_percent=volatility_percent,
            candles_analyzed=len(ordered),
        )

    def _metadata(
        self,
        features: FeatureSummary | None,
        reason: str,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "model_version": self.model_version,
            "simulation_only": True,
            "safety_notice": SAFETY_NOTICE,
            "reason": reason,
        }
        if features is not None:
            metadata["features"] = features.as_dict()
        else:
            metadata["features"] = {}
        if extra:
            metadata.update(extra)
        return metadata

    def _hold_signal(
        self,
        symbol: str,
        timeframe: str,
        entry: float,
        reason: str,
        features: FeatureSummary | None = None,
    ) -> TradingSignal:
        return TradingSignal(
            symbol=symbol,
            timeframe=timeframe,
            direction="hold",
            strategy="ai_trader_simulation",
            confidence=0.0,
            entry=entry,
            stop_loss=entry,
            take_profit=entry,
            reason=reason,
            metadata=self._metadata(features, reason),
        )

    def generate_signal(
        self,
        candles: list[Candle],
        symbol: str = "XAUUSD",
        timeframe: str = "M5",
        min_confidence: float = 0.55,
    ) -> TradingSignal:
        if not candles:
            return self._hold_signal(
                symbol=symbol,
                timeframe=timeframe,
                entry=1.0,
                reason="insufficient candles: no candle data supplied",
            )

        ordered = sorted(candles, key=lambda item: item.timestamp)
        latest_close = ordered[-1].close
        features = self.compute_features(ordered)
        if features is None:
            return self._hold_signal(
                symbol=symbol,
                timeframe=timeframe,
                entry=latest_close,
                reason="insufficient candles: at least 21 candles are required",
            )

        trend_delta = features.fast_ma - features.slow_ma
        trend_strength = abs(trend_delta) / max(features.atr_proxy, 0.01)
        momentum_strength = abs(features.momentum_3) / max(features.atr_proxy, 0.01)
        confidence = self._clamp(0.35 + (trend_strength * 0.18) + (momentum_strength * 0.08))

        direction: str = "hold"
        if trend_delta > 0 and features.momentum_3 > 0:
            direction = "buy"
        elif trend_delta < 0 and features.momentum_3 < 0:
            direction = "sell"

        if confidence < min_confidence:
            return TradingSignal(
                symbol=symbol,
                timeframe=timeframe,
                direction="hold",
                strategy="ai_trader_simulation",
                confidence=round(confidence, 4),
                entry=latest_close,
                stop_loss=latest_close,
                take_profit=latest_close,
                reason=f"confidence {confidence:.2f} is below min_confidence {min_confidence:.2f}",
                metadata=self._metadata(
                    features,
                    "confidence below minimum threshold",
                    {"min_confidence": min_confidence},
                ),
            )

        if direction == "hold":
            return TradingSignal(
                symbol=symbol,
                timeframe=timeframe,
                direction="hold",
                strategy="ai_trader_simulation",
                confidence=round(confidence, 4),
                entry=latest_close,
                stop_loss=latest_close,
                take_profit=latest_close,
                reason="trend and momentum are not aligned",
                metadata=self._metadata(features, "trend and momentum are not aligned"),
            )

        risk_distance = max(features.atr_proxy * 1.5, latest_close * 0.001)
        reward_distance = risk_distance * 2.0
        if direction == "buy":
            stop_loss = latest_close - risk_distance
            take_profit = latest_close + reward_distance
        else:
            stop_loss = latest_close + risk_distance
            take_profit = latest_close - reward_distance

        return TradingSignal(
            symbol=symbol,
            timeframe=timeframe,
            direction=direction,
            strategy="ai_trader_simulation",
            confidence=round(confidence, 4),
            entry=latest_close,
            stop_loss=round(stop_loss, 4),
            take_profit=round(take_profit, 4),
            reason="deterministic MA/momentum/volatility simulation signal",
            metadata=self._metadata(
                features,
                "deterministic feature logic generated signal",
                {"min_confidence": min_confidence},
            ),
        )

    def generate_decision(
        self,
        candles: list[Candle],
        symbol: str = "XAUUSD",
        timeframe: str = "M5",
        min_confidence: float = 0.55,
    ) -> dict[str, Any]:
        signal = self.generate_signal(
            candles=candles,
            symbol=symbol,
            timeframe=timeframe,
            min_confidence=min_confidence,
        )
        validation = self.trading_service.validate_signal(signal)
        features = signal.metadata.get("features", {})
        return {
            "signal": signal,
            "validation": validation,
            "feature_summary": features,
            "model_version": self.model_version,
            "simulation_only": True,
            "safety_notice": SAFETY_NOTICE,
        }

    def paper_trade(
        self,
        candles: list[Candle],
        symbol: str = "XAUUSD",
        timeframe: str = "M5",
        min_confidence: float = 0.55,
        snapshot: AccountSnapshot | None = None,
    ) -> dict[str, TradingSignal | SignalValidationResult | ExecutionResult | dict[str, Any] | str | bool]:
        decision = self.generate_decision(
            candles=candles,
            symbol=symbol,
            timeframe=timeframe,
            min_confidence=min_confidence,
        )
        signal = decision["signal"]
        request_payload: dict[str, Any] | ExecutionRequest
        if snapshot is None:
            request_payload = ExecutionRequest(signal=signal, dry_run=True, confirmation=False)
        else:
            request_payload = {
                "signal": signal,
                "dry_run": True,
                "confirmation": False,
                "snapshot": snapshot,
            }
        execution = self.trading_service.execution_engine.execute(request_payload)
        if not execution.dry_run:
            execution = execution.model_copy(
                update={
                    "dry_run": True,
                    "status": "blocked_by_config",
                    "message": "AI trader forcibly blocks non-dry-run execution.",
                }
            )
        return {
            **decision,
            "execution": execution,
            "dry_run": True,
        }
