from __future__ import annotations

import itertools
from datetime import datetime, timezone
from uuid import uuid4

from app.backtesting.models import BacktestRequest, OptimizationRequest, OptimizationResult
from app.backtesting.strategy_lab import StrategyLab


class ParameterOptimizer:
    SORT_METRICS = {"profit_factor", "net_profit_percent", "win_rate", "expectancy", "sharpe_like_score"}

    def __init__(self, strategy_lab: StrategyLab | None = None) -> None:
        self.lab = strategy_lab or StrategyLab()

    def expand_grid(self, parameter_grid: dict) -> list[dict]:
        keys = list(parameter_grid.keys())
        vals = [parameter_grid[k] for k in keys]
        return [dict(zip(keys, combo)) for combo in itertools.product(*vals)]

    def optimize(self, request: OptimizationRequest) -> OptimizationResult:
        started = datetime.now(timezone.utc)
        combos = self.expand_grid(request.parameter_grid)
        warnings: list[str] = []
        total = len(combos)
        if total > request.max_combinations:
            warnings.append(f"Combinations truncated from {total} to {request.max_combinations}")
            combos = combos[: request.max_combinations]
        sort_metric = request.sort_metric if request.sort_metric in self.SORT_METRICS else "profit_factor"
        if sort_metric != request.sort_metric:
            warnings.append("Unsupported sort metric, defaulted to profit_factor")
        results = []
        for params in combos:
            results.append(self.lab.run_backtest(BacktestRequest(strategy=request.strategy, symbol=request.symbol, timeframe=request.timeframe, dataset=request.dataset, initial_balance=request.initial_balance, parameters=params)))
        results.sort(key=lambda r: getattr(r.metrics, sort_metric), reverse=True)
        finished = datetime.now(timezone.utc)
        return OptimizationResult(id=str(uuid4()), request=request, ranked_results=results, best_result=results[0] if results else None, sort_metric=sort_metric, total_combinations=total, executed_combinations=len(combos), started_at=started, finished_at=finished, duration_ms=int((finished-started).total_seconds()*1000), warnings=warnings)
