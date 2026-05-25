from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.backtesting.datasets import DatasetProvider
from app.backtesting.metrics import BacktestMetricsCalculator
from app.backtesting.models import BacktestRequest, BacktestResult, SimulatedTrade
from app.backtesting.strategies import OBAggressiveStrategy, OBConservativeStrategy, TrendFollowStrategy


class StrategyLab:
    def __init__(self) -> None:
        self._strategies = {"ob_aggressive": OBAggressiveStrategy(), "ob_conservative": OBConservativeStrategy(), "trend_follow": TrendFollowStrategy()}
        self._datasets = DatasetProvider()
        self._metrics = BacktestMetricsCalculator()

    def list_strategies(self) -> list[dict]:
        return [{"name": s.name, "description": s.get_description(), "default_parameters": s.default_parameters} for s in self._strategies.values()]

    def get_strategy(self, name: str):
        if name not in self._strategies:
            raise ValueError(f"Unknown strategy: {name}")
        return self._strategies[name]

    def run_backtest(self, request: BacktestRequest) -> BacktestResult:
        started = datetime.now(timezone.utc)
        candles = self._datasets.load(request.dataset, request.symbol, request.timeframe)
        strategy = self.get_strategy(request.strategy)
        params = strategy.validate_parameters(request.parameters)
        balance = request.initial_balance
        equity_curve = [(candles[0].timestamp, balance)]
        trades: list[SimulatedTrade] = []
        spread = request.spread_points * 0.01
        slippage = request.slippage_points * 0.01

        for i, c in enumerate(candles):
            sig = strategy.generate_signal(candles, i, params)
            if sig.direction == "hold":
                continue
            risk_amt = balance * request.risk_per_trade_percent / 100
            stop_dist = abs(sig.entry - sig.stop_loss)
            if stop_dist <= 0 or ((sig.direction == "buy" and sig.take_profit <= sig.entry) or (sig.direction == "sell" and sig.take_profit >= sig.entry)):
                trades.append(SimulatedTrade(id=str(uuid4()), symbol=request.symbol, timeframe=request.timeframe, strategy=request.strategy, direction="buy", entry_time=c.timestamp, entry_price=sig.entry, stop_loss=sig.stop_loss, take_profit=sig.take_profit, size=0, status="skipped", exit_reason="invalid_signal"))
                continue
            size = risk_amt / stop_dist
            entry = sig.entry + spread + slippage if sig.direction == "buy" else sig.entry - spread - slippage
            trade = SimulatedTrade(id=str(uuid4()), symbol=request.symbol, timeframe=request.timeframe, strategy=request.strategy, direction=sig.direction, entry_time=c.timestamp, entry_price=entry, stop_loss=sig.stop_loss, take_profit=sig.take_profit, size=size, status="open")
            exit_price = candles[-1].close
            exit_reason = "end_of_data"
            exit_time = candles[-1].timestamp
            for j in range(i + 1, len(candles)):
                rc = candles[j]
                if sig.direction == "buy":
                    tp_hit = rc.high >= sig.take_profit
                    sl_hit = rc.low <= sig.stop_loss
                else:
                    tp_hit = rc.low <= sig.take_profit
                    sl_hit = rc.high >= sig.stop_loss
                if tp_hit and sl_hit:
                    exit_price, exit_reason, exit_time = sig.stop_loss, "stop_loss", rc.timestamp
                    break
                if sl_hit:
                    exit_price, exit_reason, exit_time = sig.stop_loss, "stop_loss", rc.timestamp
                    break
                if tp_hit:
                    exit_price, exit_reason, exit_time = sig.take_profit, "take_profit", rc.timestamp
                    break
            trade.exit_price = exit_price
            trade.exit_time = exit_time
            trade.exit_reason = exit_reason
            trade.status = "closed"
            trade.pnl = ((exit_price - trade.entry_price) if trade.direction == "buy" else (trade.entry_price - exit_price)) * trade.size - request.commission_per_trade
            trade.pnl_percent = (trade.pnl / request.initial_balance) * 100
            trade.rr = abs((exit_price - trade.entry_price) / (trade.entry_price - trade.stop_loss)) if (trade.entry_price - trade.stop_loss) != 0 else 0
            balance += trade.pnl
            equity_curve.append((exit_time, balance))
            trades.append(trade)

        finished = datetime.now(timezone.utc)
        metrics = self._metrics.calculate(trades, request.initial_balance, balance, equity_curve)
        return BacktestResult(id=str(uuid4()), request=request, strategy=request.strategy, symbol=request.symbol, timeframe=request.timeframe, initial_balance=request.initial_balance, final_balance=round(balance, 4), metrics=metrics, trades=trades, parameters=params, started_at=started, finished_at=finished, duration_ms=int((finished - started).total_seconds() * 1000))
