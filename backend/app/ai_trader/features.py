from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.trading.models import Candle


@dataclass(frozen=True)
class AITraderFeatures:
    close: float = 0.0
    fast_ma: float = 0.0
    slow_ma: float = 0.0
    ma_delta: float = 0.0
    momentum_3: float = 0.0
    momentum_7: float = 0.0
    volatility_pct: float = 0.0
    atr_proxy: float = 0.0
    volume_ma: float = 0.0
    volume_ratio: float = 0.0
    trend_state: str = "unknown"
    volatility_state: str = "unknown"
    candles_analyzed: int = 0
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "close": self.close,
            "fast_ma": self.fast_ma,
            "slow_ma": self.slow_ma,
            "ma_delta": self.ma_delta,
            "momentum_3": self.momentum_3,
            "momentum_7": self.momentum_7,
            "volatility_pct": self.volatility_pct,
            "atr_proxy": self.atr_proxy,
            "volume_ma": self.volume_ma,
            "volume_ratio": self.volume_ratio,
            "trend_state": self.trend_state,
            "volatility_state": self.volatility_state,
            "candles_analyzed": self.candles_analyzed,
        }


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    if result != result or result in {float("inf"), float("-inf")}:  # NaN/Inf guard
        return default
    return result


def _mean(values: list[float]) -> float:
    clean = [value for value in values if value == value]
    return sum(clean) / len(clean) if clean else 0.0


def _safe_range(candle: Candle) -> float:
    high = max(_safe_float(candle.high), 0.0)
    low = max(_safe_float(candle.low), 0.0)
    open_price = max(_safe_float(candle.open), 0.0)
    close = max(_safe_float(candle.close), 0.0)
    return max(high - low, abs(close - open_price), 0.0)


def _trend_state(ma_delta: float, atr_proxy: float) -> str:
    threshold = max(atr_proxy * 0.25, 0.0001)
    if ma_delta > threshold:
        return "up"
    if ma_delta < -threshold:
        return "down"
    return "flat"


def _volatility_state(volatility_pct: float) -> str:
    if volatility_pct >= 0.35:
        return "high"
    if volatility_pct >= 0.12:
        return "normal"
    return "low"


def calculate_features(
    candles: list[Candle],
    min_candles: int = 21,
    fast_window: int = 7,
    slow_window: int = 21,
) -> AITraderFeatures:
    warnings: list[str] = []
    if not candles:
        return AITraderFeatures(warnings=["no candle data supplied"])

    try:
        ordered = sorted(candles, key=lambda item: item.timestamp)
    except Exception:
        ordered = list(candles)
        warnings.append("could not sort candles by timestamp")

    clean: list[Candle] = []
    for candle in ordered:
        close = _safe_float(getattr(candle, "close", 0.0))
        high = _safe_float(getattr(candle, "high", close))
        low = _safe_float(getattr(candle, "low", close))
        open_price = _safe_float(getattr(candle, "open", close))
        if close <= 0 or high < 0 or low < 0 or open_price < 0:
            warnings.append("ignored malformed candle with non-positive price")
            continue
        clean.append(candle)

    if not clean:
        return AITraderFeatures(warnings=[*warnings, "no valid candles after sanitization"])

    if len(clean) < min_candles:
        warnings.append(f"insufficient candles: need {min_candles}, got {len(clean)}")

    closes = [_safe_float(c.close) for c in clean]
    volumes = [_safe_float(getattr(c, "volume", 0.0)) for c in clean]
    latest = clean[-1]
    close = _safe_float(latest.close)
    fast_values = closes[-min(fast_window, len(closes)) :]
    slow_values = closes[-min(slow_window, len(closes)) :]
    fast_ma = _mean(fast_values)
    slow_ma = _mean(slow_values)
    ma_delta = fast_ma - slow_ma
    momentum_3 = close - closes[-4] if len(closes) >= 4 else 0.0
    momentum_7 = close - closes[-8] if len(closes) >= 8 else 0.0
    ranges = [_safe_range(candle) for candle in clean[-min(slow_window, len(clean)) :]]
    atr_proxy = max(_mean(ranges), close * 0.0005, 0.01)
    volatility_pct = (atr_proxy / close) * 100 if close > 0 else 0.0
    volume_ma = _mean(volumes[-min(slow_window, len(volumes)) :])
    latest_volume = volumes[-1] if volumes else 0.0
    volume_ratio = latest_volume / volume_ma if volume_ma > 0 else 0.0

    return AITraderFeatures(
        close=close,
        fast_ma=fast_ma,
        slow_ma=slow_ma,
        ma_delta=ma_delta,
        momentum_3=momentum_3,
        momentum_7=momentum_7,
        volatility_pct=volatility_pct,
        atr_proxy=atr_proxy,
        volume_ma=volume_ma,
        volume_ratio=volume_ratio,
        trend_state=_trend_state(ma_delta, atr_proxy),
        volatility_state=_volatility_state(volatility_pct),
        candles_analyzed=len(clean),
        warnings=warnings,
    )
