from app.core.config import get_settings
from app.trading.funnel_filter import FunnelFilter
from app.trading.mt5_adapter import MT5Adapter
from app.trading.risk_models import Signal


class XAUScanner:
    def __init__(self, mt5: MT5Adapter | None = None) -> None:
        self.settings = get_settings()
        self.mt5 = mt5 or MT5Adapter()
        self.filter = FunnelFilter()

    def scan(self) -> Signal:
        candles = self.mt5.get_candles(self.settings.trading_symbol, self.settings.trading_timeframe)
        state = self.filter.evaluate(candles)
        last = candles[-1].close

        if state['direction'] == 'buy':
            entry = (round(last - 0.3, 4), round(last - 0.1, 4))
            sl = round(last - 1.5, 4)
            tp = round(last + 3.0, 4)
            confidence = 0.68
        elif state['direction'] == 'sell':
            entry = (round(last + 0.1, 4), round(last + 0.3, 4))
            sl = round(last + 1.5, 4)
            tp = round(last - 3.0, 4)
            confidence = 0.66
        else:
            entry = (round(last - 0.1, 4), round(last + 0.1, 4))
            sl = round(last - 1.0, 4)
            tp = round(last + 1.0, 4)
            confidence = 0.5

        return Signal(
            symbol=self.settings.trading_symbol,
            timeframe=self.settings.trading_timeframe,
            direction=state['direction'],
            entry_zone=entry,
            stop_loss=sl,
            take_profit=tp,
            confidence=confidence,
            strategy=self.settings.primary_strategy,
            filter_state=state,
        )
