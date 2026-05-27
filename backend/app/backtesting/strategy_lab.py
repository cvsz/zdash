from __future__ import annotations

from datetime import datetime, timezone
from math import isfinite
from typing import Any, cast
from uuid import uuid4

from app.backtesting.datasets import DatasetProvider
from app.backtesting.metrics import BacktestMetricsCalculator
from app.backtesting.models import (
    BacktestRequest,
    BacktestResult,
    SimulatedTrade,
    StrategySignal,
)
from app.backtesting.strategies import (
    OBAggressiveStrategy,
    OBConservativeStrategy,
    TrendFollowStrategy,
)
from app.core.events import event_bus


class StrategyLab:
    def __init__(self) -> None:
        self._strategies = {
            "ob_aggressive": OBAggressiveStrategy(),
            "ob_conservative": OBConservativeStrategy(),
            "trend_follow": TrendFollowStrategy(),
        }
        self._datasets = DatasetProvider()
        self._metrics = BacktestMetricsCalculator()

    def list_strategies(self) -> list[dict]:
        return [
            {
                "name": strategy.name,
                "description": strategy.get_description(),
                "default_parameters": strategy.default_parameters,
            }
            for strategy in self._strategies.values()
        ]

    def get_strategy(self, name: str):
        if name not in self._strategies:
            raise ValueError(f"Unknown strategy: {name}")
        return self._strategies[name]

    def run_backtest(self, request: BacktestRequest) -> BacktestResult:
        started = datetime.now(timezone.utc)
        candles = self._datasets.load(
            request.dataset, request.symbol, request.timeframe
        )
        if not candles:
            raise ValueError("Dataset returned no candles")

        strategy = self.get_strategy(request.strategy)
        params = strategy.validate_parameters(request.parameters)
        balance = request.initial_balance
        equity_curve = [(candles[0].timestamp, balance)]
        trades: list[SimulatedTrade] = []
        spread = _points_to_price(request.spread_points)
        slippage = _points_to_price(request.slippage_points)

        index = 0
        while index < len(candles):
            candle = candles[index]
            signal = strategy.generate_signal(candles, index, params)

            if signal.direction == "hold":
                index += 1
                continue

            event_bus.emit(
                "strategy.signal.generated",
                "strategy_lab",
                "Strategy signal generated",
                {
                    "strategy": request.strategy,
                    "symbol": request.symbol,
                    "timeframe": request.timeframe,
                    "index": index,
                    "direction": signal.direction,
                    "confidence": signal.confidence,
                },
            )

            if not _is_valid_signal(signal):
                trades.append(
                    SimulatedTrade(
                        id=str(uuid4()),
                        symbol=request.symbol,
                        timeframe=request.timeframe,
                        strategy=request.strategy,
                        direction=signal.direction,
                        entry_time=candle.timestamp,
                        exit_time=candle.timestamp,
                        entry_price=signal.entry,
                        exit_price=signal.entry,
                        stop_loss=signal.stop_loss,
                        take_profit=signal.take_profit,
                        size=0.0,
                        pnl=0.0,
                        pnl_percent=0.0,
                        rr=0.0,
                        status="skipped",
                        exit_reason="invalid_signal",
                        metadata={"reason": "invalid_signal_levels"},
                    )
                )
                event_bus.emit(
                    "strategy.signal.skipped",
                    "strategy_lab",
                    "Strategy signal skipped",
                    {
                        "strategy": request.strategy,
                        "index": index,
                        "reason": "invalid_signal",
                    },
                )
                index += 1
                continue

            risk_amount = balance * (request.risk_per_trade_percent / 100.0)
            stop_distance = abs(signal.entry - signal.stop_loss)
            if risk_amount <= 0 or stop_distance <= 0:
                event_bus.emit(
                    "strategy.signal.skipped",
                    "strategy_lab",
                    "Strategy signal skipped",
                    {
                        "strategy": request.strategy,
                        "index": index,
                        "reason": "invalid_risk_setup",
                    },
                )
                index += 1
                continue

            entry_price = (
                signal.entry + spread + slippage
                if signal.direction == "buy"
                else signal.entry - spread - slippage
            )
            position_size = risk_amount / stop_distance

            trade = SimulatedTrade(
                id=str(uuid4()),
                symbol=request.symbol,
                timeframe=request.timeframe,
                strategy=request.strategy,
                direction=signal.direction,
                entry_time=candle.timestamp,
                entry_price=entry_price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                size=position_size,
                status="open",
            )

            exit_index, exit_price, exit_reason = self._find_exit(
                candles=candles,
                start_index=index + 1,
                signal=signal,
                spread=spread,
                slippage=slippage,
            )

            if exit_index is None:
                exit_index = len(candles) - 1
            exit_candle = candles[exit_index]
            trade.exit_time = exit_candle.timestamp
            trade.exit_price = exit_price
            trade.exit_reason = cast(Any, exit_reason)
            trade.status = "closed"

            raw_pnl = (
                (trade.exit_price - trade.entry_price)
                if trade.direction == "buy"
                else (trade.entry_price - trade.exit_price)
            ) * trade.size
            trade.pnl = raw_pnl - request.commission_per_trade
            trade.pnl_percent = (
                (trade.pnl / request.initial_balance * 100.0)
                if request.initial_balance
                else 0.0
            )
            trade.rr = (trade.pnl / risk_amount) if risk_amount > 0 else 0.0

            balance += trade.pnl
            equity_curve.append((trade.exit_time, balance))
            trades.append(trade)

            # Phase 05 rule: do not allow overlapping trades unless explicitly
            # configured.
            index = exit_index + 1

        finished = datetime.now(timezone.utc)
        metrics = self._metrics.calculate(
            trades, request.initial_balance, balance, equity_curve
        )
        return BacktestResult(
            id=str(uuid4()),
            request=request,
            strategy=request.strategy,
            symbol=request.symbol,
            timeframe=request.timeframe,
            initial_balance=request.initial_balance,
            final_balance=round(balance, 4),
            metrics=metrics,
            trades=trades,
            parameters=params,
            started_at=started,
            finished_at=finished,
            duration_ms=max(0, int((finished - started).total_seconds() * 1000)),
            warnings=[],
        )

    def _find_exit(
        self,
        candles: list,
        start_index: int,
        signal: StrategySignal,
        spread: float,
        slippage: float,
    ) -> tuple[int | None, float, str]:
        last_candle = candles[-1]
        fallback_exit = last_candle.close
        if signal.direction == "buy":
            fallback_exit -= spread + slippage
        else:
            fallback_exit += spread + slippage

        for index in range(start_index, len(candles)):
            candle = candles[index]
            if signal.direction == "buy":
                tp_hit = candle.high >= signal.take_profit
                sl_hit = candle.low <= signal.stop_loss
                if tp_hit and sl_hit:
                    return (
                        index,
                        max(signal.stop_loss - spread - slippage, 1e-6),
                        "stop_loss",
                    )
                if sl_hit:
                    return (
                        index,
                        max(signal.stop_loss - spread - slippage, 1e-6),
                        "stop_loss",
                    )
                if tp_hit:
                    return (
                        index,
                        max(signal.take_profit - spread - slippage, 1e-6),
                        "take_profit",
                    )
            elif signal.direction == "sell":
                tp_hit = candle.low <= signal.take_profit
                sl_hit = candle.high >= signal.stop_loss
                if tp_hit and sl_hit:
                    return (
                        index,
                        max(signal.stop_loss + spread + slippage, 1e-6),
                        "stop_loss",
                    )
                if sl_hit:
                    return (
                        index,
                        max(signal.stop_loss + spread + slippage, 1e-6),
                        "stop_loss",
                    )
                if tp_hit:
                    return (
                        index,
                        max(signal.take_profit + spread + slippage, 1e-6),
                        "take_profit",
                    )

        return len(candles) - 1, max(fallback_exit, 1e-6), "end_of_data"


def _is_valid_signal(signal: StrategySignal) -> bool:
    if signal.direction not in {"buy", "sell"}:
        return False
    if (
        not isfinite(signal.entry)
        or not isfinite(signal.stop_loss)
        or not isfinite(signal.take_profit)
    ):
        return False
    if signal.entry <= 0 or signal.stop_loss <= 0 or signal.take_profit <= 0:
        return False
    if signal.direction == "buy":
        return signal.stop_loss < signal.entry < signal.take_profit
    return signal.take_profit < signal.entry < signal.stop_loss


def _points_to_price(points: float) -> float:
    return max(points, 0.0) * 0.01
