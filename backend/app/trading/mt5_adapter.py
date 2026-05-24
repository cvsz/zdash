from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

from app.core.config import get_settings
from app.trading.risk_models import Candle


class MT5AdapterBase(ABC):
    @abstractmethod
    def status(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_candles(self, symbol: str, timeframe: str, count: int = 120) -> list[Candle]:
        raise NotImplementedError

    @abstractmethod
    def diagnostics(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def symbol_available(self, symbol: str) -> bool:
        raise NotImplementedError


class MT5Adapter(MT5AdapterBase):
    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        return all([self.settings.mt5_login, self.settings.mt5_password, self.settings.mt5_server])

    def status(self) -> dict:
        return {
            'configured': self.is_configured(),
            'connected': False,
            'mode': 'mock' if not self.is_configured() else 'adapter-shell',
        }

    def diagnostics(self) -> dict:
        return {
            'configured': self.is_configured(),
            'login_present': bool(self.settings.mt5_login),
            'password_present': bool(self.settings.mt5_password),
            'server_present': bool(self.settings.mt5_server),
            'path_present': bool(self.settings.mt5_path),
        }

    def symbol_available(self, symbol: str) -> bool:
        supported = {'XAUUSD', 'EURUSD', 'GBPUSD'}
        return symbol.upper() in supported

    def get_candles(self, symbol: str, timeframe: str, count: int = 120) -> list[Candle]:
        now = datetime.now(timezone.utc)
        base = 2350.0
        candles: list[Candle] = []
        for i in range(count):
            drift = (i - count / 2) * 0.08
            o = base + drift
            c = o + (0.35 if i % 2 == 0 else -0.2)
            h = max(o, c) + 0.25
            l = min(o, c) - 0.25
            candles.append(
                Candle(
                    timestamp=(now - timedelta(minutes=(count - i) * 5)).isoformat(),
                    open=round(o, 4),
                    high=round(h, 4),
                    low=round(l, 4),
                    close=round(c, 4),
                    volume=100 + i,
                )
            )
        return candles
