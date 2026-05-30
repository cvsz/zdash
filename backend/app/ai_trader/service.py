from __future__ import annotations

from typing import Any

from app.ai_trader.features import AITraderFeatures, calculate_features
from app.ai_trader.registry import (
    AITraderStrategy,
    get_strategy,
    list_strategies,
    resolve_strategy,
)
from app.core.events import event_bus
from app.risk.models import AccountSnapshot
from app.trading.models import (
    Candle,
    ExecutionRequest,
    ExecutionResult,
    SignalValidationResult,
    TradingSignal,
)
from app.trading.trading_service import TradingService

MODEL_VERSION = "ai-trader-phase35"
SAFETY_NOTICE = "Simulation only. Not financial advice. No live execution."
RISK_POLICY = {
    "dry_run_forced": True,
    "guardian_required": True,
    "live_execution_allowed": False,
}


class AITraderService:
    """Simulation-only AI Trader control-plane service."""

    def __init__(self, trading_service: TradingService | None = None) -> None:
        self.trading_service = trading_service or TradingService()
        self.model_version = MODEL_VERSION

    def list_strategies(self) -> list[AITraderStrategy]:
        return list_strategies()

    def get_strategy(self, strategy_id: str) -> AITraderStrategy | None:
        return get_strategy(strategy_id)

    def resolve_strategy(self, strategy_id: str | None) -> AITraderStrategy:
        return resolve_strategy(strategy_id)

    @staticmethod
    def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
        return max(low, min(high, value))

    def build_safety_metadata(
        self,
        strategy: AITraderStrategy,
        features: AITraderFeatures,
        warnings: list[str],
        explanation: str,
    ) -> dict[str, Any]:
        return {
            "model_version": self.model_version,
            "strategy_id": strategy.id,
            "simulation_only": True,
            "safety_notice": SAFETY_NOTICE,
            "features": features.as_dict(),
            "warnings": warnings,
            "explanation": explanation,
            "risk_policy": dict(RISK_POLICY),
        }

    def explain_decision(
        self,
        strategy: AITraderStrategy,
        direction: str,
        confidence: float,
        features: AITraderFeatures,
        warnings: list[str],
    ) -> str:
        base = (
            f"{strategy.name} produced {direction.upper()} with confidence "
            f"{confidence:.2f}. Trend={features.trend_state}, "
            f"volatility={features.volatility_state}, momentum_3={features.momentum_3:.4f}."
        )
        if warnings:
            return f"{base} Warnings: {'; '.join(warnings)}."
        return base

    def _confidence(self, features: AITraderFeatures, multiplier: float = 1.0) -> float:
        trend_strength = abs(features.ma_delta) / max(features.atr_proxy, 0.01)
        momentum_strength = (
            abs(features.momentum_3) + abs(features.momentum_7) * 0.5
        ) / max(features.atr_proxy, 0.01)
        volatility_factor = 0.85 if features.volatility_state == "high" else 1.0
        return self._clamp(
            (0.35 + trend_strength * 0.12 + momentum_strength * 0.05)
            * multiplier
            * volatility_factor
        )

    def _trend_momentum(
        self, features: AITraderFeatures
    ) -> tuple[str, float, list[str]]:
        confidence = self._confidence(features)
        if features.fast_ma > features.slow_ma and features.momentum_3 > 0:
            return "buy", confidence, []
        if features.fast_ma < features.slow_ma and features.momentum_3 < 0:
            return "sell", confidence, []
        return "hold", min(confidence, 0.5), ["trend and momentum are not aligned"]

    def _mean_reversion(
        self, features: AITraderFeatures
    ) -> tuple[str, float, list[str]]:
        warnings: list[str] = []
        if features.volatility_state == "high":
            return "hold", 0.35, ["volatility too high for mean reversion simulation"]
        distance = features.close - features.slow_ma
        confidence = self._confidence(features, 0.9)
        if distance < -features.atr_proxy and features.momentum_3 >= 0:
            return "buy", confidence, warnings
        if distance > features.atr_proxy and features.momentum_3 <= 0:
            return "sell", confidence, warnings
        return (
            "hold",
            min(confidence, 0.52),
            ["price extension is not sufficient for mean reversion"],
        )

    def _volatility_breakout(
        self, features: AITraderFeatures
    ) -> tuple[str, float, list[str]]:
        if features.volatility_state not in {"normal", "high"}:
            return "hold", 0.3, ["volatility is too low for breakout simulation"]
        confidence = self._confidence(features, 1.05)
        if features.momentum_7 > features.atr_proxy and features.trend_state == "up":
            return "buy", confidence, []
        if features.momentum_7 < -features.atr_proxy and features.trend_state == "down":
            return "sell", confidence, []
        return "hold", min(confidence, 0.55), ["volatility and momentum do not agree"]

    def _conservative_guarded(
        self, features: AITraderFeatures
    ) -> tuple[str, float, list[str]]:
        warnings: list[str] = []
        if features.volatility_state == "high":
            return "hold", 0.25, ["conservative strategy blocks high volatility"]
        direction, confidence, base_warnings = self._trend_momentum(features)
        confidence = self._clamp(confidence * 0.9)
        if abs(features.momentum_7) < features.atr_proxy:
            direction = "hold"
            warnings.append("seven-candle momentum is not strong enough")
        return direction, confidence, [*base_warnings, *warnings]

    def _strategy_decision(
        self,
        strategy: AITraderStrategy,
        features: AITraderFeatures,
    ) -> tuple[str, float, list[str]]:
        if strategy.id == "mean_reversion_v1":
            return self._mean_reversion(features)
        if strategy.id == "volatility_breakout_v1":
            return self._volatility_breakout(features)
        if strategy.id == "conservative_guarded_v1":
            return self._conservative_guarded(features)
        return self._trend_momentum(features)

    def _build_signal(
        self,
        symbol: str,
        timeframe: str,
        strategy: AITraderStrategy,
        features: AITraderFeatures,
        direction: str,
        confidence: float,
        warnings: list[str],
        min_confidence: float,
    ) -> TradingSignal:
        all_warnings = [*features.warnings, *warnings]
        if features.candles_analyzed < strategy.min_candles:
            direction = "hold"
            confidence = min(confidence, 0.2)
            all_warnings.append(
                f"insufficient candles for {strategy.id}: need {strategy.min_candles}, got {features.candles_analyzed}"
            )
        if confidence < min_confidence:
            direction = "hold"
            all_warnings.append(
                f"confidence {confidence:.2f} below min_confidence {min_confidence:.2f}"
            )

        entry = features.close if features.close > 0 else 1.0
        risk_distance = max(features.atr_proxy * 1.5, entry * 0.001, 0.01)
        reward_distance = risk_distance * 2.0
        if direction == "buy":
            stop_loss = entry - risk_distance
            take_profit = entry + reward_distance
        elif direction == "sell":
            stop_loss = entry + risk_distance
            take_profit = entry - reward_distance
        else:
            stop_loss = entry
            take_profit = entry

        explanation = self.explain_decision(
            strategy=strategy,
            direction=direction,
            confidence=confidence,
            features=features,
            warnings=all_warnings,
        )
        metadata = self.build_safety_metadata(
            strategy, features, all_warnings, explanation
        )
        return TradingSignal(
            symbol=symbol,
            timeframe=timeframe,
            direction=direction,
            strategy=strategy.id,
            confidence=round(confidence, 4),
            entry=round(entry, 4),
            stop_loss=round(stop_loss, 4),
            take_profit=round(take_profit, 4),
            reason=explanation,
            metadata=metadata,
        )

    def generate_signal(
        self,
        candles: list[Candle],
        symbol: str = "XAUUSD",
        timeframe: str = "M5",
        min_confidence: float | None = None,
        strategy_id: str | None = None,
    ) -> TradingSignal:
        strategy = self.resolve_strategy(strategy_id)
        threshold = (
            min_confidence
            if min_confidence is not None
            else strategy.default_min_confidence
        )
        features = calculate_features(candles, min_candles=strategy.min_candles)
        direction, confidence, warnings = self._strategy_decision(strategy, features)
        signal = self._build_signal(
            symbol=symbol,
            timeframe=timeframe,
            strategy=strategy,
            features=features,
            direction=direction,
            confidence=confidence,
            warnings=warnings,
            min_confidence=threshold,
        )
        event_bus.emit(
            "ai_trader.signal.generated",
            "ai_trader.service",
            "AI trader simulation signal generated",
            self._event_payload(signal),
        )
        return signal

    def generate_decision(
        self,
        candles: list[Candle],
        symbol: str = "XAUUSD",
        timeframe: str = "M5",
        min_confidence: float | None = None,
        strategy_id: str | None = None,
    ) -> dict[str, Any]:
        signal = self.generate_signal(
            candles=candles,
            symbol=symbol,
            timeframe=timeframe,
            min_confidence=min_confidence,
            strategy_id=strategy_id,
        )
        validation = self.trading_service.validate_signal(signal)
        return {
            "signal": signal,
            "validation": validation,
            "features": signal.metadata.get("features", {}),
            "feature_summary": signal.metadata.get("features", {}),
            "warnings": signal.metadata.get("warnings", []),
            "explanation": signal.metadata.get("explanation", signal.reason),
            "model_version": self.model_version,
            "simulation_only": True,
            "safety_notice": SAFETY_NOTICE,
            "risk_policy": dict(RISK_POLICY),
        }

    def compare_strategies(
        self,
        candles: list[Candle],
        symbol: str = "XAUUSD",
        timeframe: str = "M5",
        strategy_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        ids = strategy_ids or [strategy.id for strategy in self.list_strategies()]
        decisions = [
            self.generate_decision(
                candles=candles,
                symbol=symbol,
                timeframe=timeframe,
                strategy_id=strategy_id,
            )
            for strategy_id in ids
        ]
        ranked = sorted(
            decisions,
            key=lambda item: (
                item["signal"].direction != "hold",
                item["signal"].confidence,
            ),
            reverse=True,
        )
        event_bus.emit(
            "ai_trader.strategy.compared",
            "ai_trader.service",
            "AI trader simulation strategies compared",
            {
                "strategy_id": ",".join(ids),
                "symbol": symbol,
                "timeframe": timeframe,
                "direction": ranked[0]["signal"].direction if ranked else "hold",
                "confidence": ranked[0]["signal"].confidence if ranked else 0.0,
                "simulation_only": True,
                "dry_run": True,
            },
        )
        return {
            "ranked_decisions": ranked,
            "model_version": self.model_version,
            "simulation_only": True,
            "safety_notice": SAFETY_NOTICE,
        }

    def paper_trade(
        self,
        candles: list[Candle],
        symbol: str = "XAUUSD",
        timeframe: str = "M5",
        min_confidence: float | None = None,
        strategy_id: str | None = None,
        snapshot: AccountSnapshot | None = None,
    ) -> dict[
        str,
        TradingSignal
        | SignalValidationResult
        | ExecutionResult
        | dict[str, Any]
        | str
        | bool
        | list[str],
    ]:
        decision = self.generate_decision(
            candles=candles,
            symbol=symbol,
            timeframe=timeframe,
            min_confidence=min_confidence,
            strategy_id=strategy_id,
        )
        signal = decision["signal"]
        event_bus.emit(
            "ai_trader.paper_trade.requested",
            "ai_trader.service",
            "AI trader dry-run paper trade requested",
            self._event_payload(signal),
        )
        request_payload: dict[str, Any] | ExecutionRequest
        if snapshot is None:
            request_payload = ExecutionRequest(
                signal=signal, dry_run=True, confirmation=False
            )
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
        completed_type = (
            "ai_trader.paper_trade.completed"
            if execution.status == "simulated"
            else "ai_trader.paper_trade.blocked"
        )
        event_bus.emit(
            completed_type,
            "ai_trader.service",
            "AI trader dry-run paper trade completed",
            {**self._event_payload(signal), "execution_status": execution.status},
        )
        return {
            **decision,
            "execution": execution,
            "dry_run": True,
            "live_execution_allowed": False,
        }

    @staticmethod
    def _event_payload(signal: TradingSignal) -> dict[str, Any]:
        return {
            "strategy_id": signal.metadata.get("strategy_id", signal.strategy),
            "symbol": signal.symbol,
            "timeframe": signal.timeframe,
            "direction": signal.direction,
            "confidence": signal.confidence,
            "simulation_only": True,
            "dry_run": True,
        }
