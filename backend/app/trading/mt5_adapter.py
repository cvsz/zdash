from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.core.config import get_settings
from app.core.events import event_bus
from app.trading.market_data import generate_mock_xauusd_m5_candles
from app.trading.models import Candle, ExecutionResult, TradingSignal


class MT5Adapter:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._mt5_module = self._try_import_mt5()

    @staticmethod
    def _try_import_mt5() -> Any | None:
        try:
            import MetaTrader5 as mt5  # type: ignore

            return mt5
        except Exception:
            return None

    def _credentials_present(self) -> bool:
        return bool(
            self.settings.mt5_login
            and self.settings.mt5_password
            and self.settings.mt5_server
        )

    def is_available(self) -> bool:
        return (
            self.settings.mt5_enabled
            and self._mt5_module is not None
            and self._credentials_present()
        )

    def connect(self) -> dict[str, Any]:
        if not self.settings.mt5_enabled:
            event_bus.emit(
                "mt5.mock.enabled",
                "MT5Adapter",
                "MT5 disabled; running mock mode",
                {"mt5_enabled": False},
            )
            return {
                "ok": True,
                "connected": False,
                "mode": "mock",
                "reason": "MT5_ENABLED=false",
            }

        if self._mt5_module is None:
            event_bus.emit(
                "mt5.connection.failed",
                "MT5Adapter",
                "MetaTrader5 package unavailable; falling back to mock",
                {"package_available": False},
            )
            return {
                "ok": False,
                "connected": False,
                "mode": "mock",
                "reason": "MetaTrader5 package unavailable",
            }

        if not self._credentials_present():
            event_bus.emit(
                "mt5.connection.failed",
                "MT5Adapter",
                "MT5 credentials missing; falling back to mock",
                {"credentials_present": False},
            )
            return {
                "ok": False,
                "connected": False,
                "mode": "mock",
                "reason": "MT5 credentials missing",
            }

        # Phase 02 shell: explicit no live connectivity handoff.
        return {
            "ok": True,
            "connected": False,
            "mode": "adapter-shell",
            "reason": "Phase 02 uses mock-safe adapter shell",
        }

    def get_candles(
        self, symbol: str, timeframe: str, limit: int = 300
    ) -> list[Candle]:
        _ = symbol, timeframe
        if not self.is_available():
            return generate_mock_xauusd_m5_candles(limit=limit)

        # Phase 02 safety policy: keep market data deterministic and offline.
        return generate_mock_xauusd_m5_candles(limit=limit)

    def get_account_snapshot(self) -> dict[str, Any]:
        return {
            "balance": 10000.0,
            "equity": 10000.0,
            "margin_free": 10000.0,
            "currency": "USD",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": "mock",
        }

    def send_order(self, signal: TradingSignal) -> ExecutionResult:
        if self.settings.dry_run:
            return ExecutionResult(
                ok=True,
                status="simulated",
                dry_run=True,
                signal=signal,
                message="Dry-run execution simulated by MT5 adapter shell.",
                simulated_order_id=f"sim-{uuid4()}",
            )

        if not self.settings.live_trading_ack:
            return ExecutionResult(
                ok=False,
                status="blocked_by_config",
                dry_run=False,
                signal=signal,
                message="LIVE_TRADING_ACK=false blocks non-dry-run execution.",
            )

        return ExecutionResult(
            ok=False,
            status="blocked_by_config",
            dry_run=False,
            signal=signal,
            message="Phase 02 foundation keeps real order routing disabled.",
        )

    # Compatibility helpers used by legacy API surfaces.
    def status(self) -> dict[str, Any]:
        probe = self.connect()
        return {
            "configured": self._credentials_present(),
            "connected": probe["connected"],
            "mode": probe["mode"],
            "reason": probe["reason"],
        }

    def diagnostics(self) -> dict[str, Any]:
        return {
            "mt5_enabled": self.settings.mt5_enabled,
            "package_available": self._mt5_module is not None,
            "credentials_present": self._credentials_present(),
            "login_present": bool(self.settings.mt5_login),
            "password_present": bool(self.settings.mt5_password),
            "server_present": bool(self.settings.mt5_server),
            "path_present": bool(self.settings.mt5_path),
        }

    @staticmethod
    def symbol_available(symbol: str) -> bool:
        return symbol.upper() in {"XAUUSD", "XAUUSDm"}
