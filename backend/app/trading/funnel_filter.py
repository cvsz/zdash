from app.trading.risk_models import Candle


def _sma(values: list[float], window: int) -> float:
    if len(values) < window:
        return values[-1]
    sample = values[-window:]
    return sum(sample) / window


class FunnelFilter:
    def __init__(self, long_window: int = 21, mid_window: int = 10, trigger_window: int = 3) -> None:
        self.long_window = long_window
        self.mid_window = mid_window
        self.trigger_window = trigger_window

    def evaluate(self, candles: list[Candle]) -> dict:
        closes = [c.close for c in candles]
        long_sma = _sma(closes, self.long_window)
        mid_sma = _sma(closes, self.mid_window)
        trigger_sma = _sma(closes, self.trigger_window)
        price = closes[-1]

        direction = 'neutral'
        if price > long_sma and trigger_sma > mid_sma:
            direction = 'buy'
        elif price < long_sma and trigger_sma < mid_sma:
            direction = 'sell'

        return {
            'direction': direction,
            'long_window': self.long_window,
            'mid_window': self.mid_window,
            'trigger_window': self.trigger_window,
            'long_sma': round(long_sma, 4),
            'mid_sma': round(mid_sma, 4),
            'trigger_sma': round(trigger_sma, 4),
            'price': round(price, 4),
        }
