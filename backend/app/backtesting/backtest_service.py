from __future__ import annotations

from app.backtesting.models import (
    BacktestRequest,
    BacktestResult,
    OptimizationRequest,
    OptimizationResult,
)
from app.backtesting.optimizer import ParameterOptimizer
from app.backtesting.promotion import StrategyPromotionGate
from app.backtesting.strategy_lab import StrategyLab
from app.core.config import get_settings
from app.core.events import event_bus


class BacktestService:
    def __init__(self) -> None:
        self.lab = StrategyLab()
        self.optimizer = ParameterOptimizer(self.lab)
        self.promotion_gate = StrategyPromotionGate()
        self.results: list[BacktestResult] = []
        self.optimization_results: list[OptimizationResult] = []

    def get_status(self) -> dict:
        settings = get_settings()
        return {
            "enabled": settings.backtesting_enabled,
            "available_strategies": self.list_strategies(),
            "stored_result_count": len(self.results),
            "stored_optimization_count": len(self.optimization_results),
            "primary_strategy_candidate": settings.primary_strategy,
            "promotion_enabled": settings.allow_strategy_promotion,
        }

    def list_strategies(self):
        return self.lab.list_strategies()

    def run_backtest(self, request: BacktestRequest) -> BacktestResult:
        settings = get_settings()
        if not settings.backtesting_enabled:
            raise ValueError("Backtesting is disabled by configuration")

        event_bus.emit(
            "backtest.started",
            "backtest_service",
            "Backtest started",
            {"strategy": request.strategy},
        )
        try:
            result = self.lab.run_backtest(request)
            self.results.insert(0, result)
            event_bus.emit(
                "backtest.completed",
                "backtest_service",
                "Backtest completed",
                {
                    "result_id": result.id,
                    "strategy": result.strategy,
                    "symbol": result.symbol,
                    "timeframe": result.timeframe,
                    "total_trades": result.metrics.total_trades,
                },
            )
            return result
        except Exception as exc:
            event_bus.emit(
                "backtest.failed",
                "backtest_service",
                "Backtest failed",
                {"error": str(exc)},
            )
            raise

    def get_results(self):
        return self.results

    def get_result(self, result_id: str):
        return next((result for result in self.results if result.id == result_id), None)

    def optimize(self, request: OptimizationRequest) -> OptimizationResult:
        settings = get_settings()
        if not settings.backtesting_enabled:
            raise ValueError("Backtesting is disabled by configuration")

        effective_max = min(
            request.max_combinations, settings.optimizer_max_combinations
        )
        effective_sort_metric = request.sort_metric or settings.optimizer_sort_metric
        normalized_request = request.model_copy(
            update={
                "max_combinations": effective_max,
                "sort_metric": effective_sort_metric,
            }
        )

        event_bus.emit(
            "optimizer.started",
            "backtest_service",
            "Optimization started",
            {"strategy": request.strategy},
        )
        try:
            result = self.optimizer.optimize(normalized_request)
            self.optimization_results.insert(0, result)
            event_bus.emit(
                "optimizer.completed",
                "backtest_service",
                "Optimization completed",
                {
                    "result_id": result.id,
                    "executed_combinations": result.executed_combinations,
                    "total_combinations": result.total_combinations,
                    "sort_metric": result.sort_metric,
                },
            )
            return result
        except Exception as exc:
            event_bus.emit(
                "optimizer.failed",
                "backtest_service",
                "Optimization failed",
                {"error": str(exc)},
            )
            raise

    def get_optimization_results(self):
        return self.optimization_results

    def evaluate_promotion(self, result_id: str):
        result = self.get_result(result_id)
        if result is None:
            raise ValueError("Result not found")

        decision = self.promotion_gate.evaluate(result)
        event_bus.emit(
            "strategy.promotion.evaluated",
            "backtest_service",
            "Promotion evaluated",
            {
                "result_id": result_id,
                "approved": decision.approved,
                "reason": decision.reason,
                "gates": decision.gates,
            },
        )
        event_bus.emit(
            "strategy.promotion.approved"
            if decision.approved
            else "strategy.promotion.rejected",
            "backtest_service",
            "Promotion decision",
            {
                "result_id": result_id,
                "strategy": result.strategy,
                "reason": decision.reason,
            },
        )
        return decision


_backtest_service: BacktestService | None = None


def get_backtest_service() -> BacktestService:
    global _backtest_service
    if _backtest_service is None:
        _backtest_service = BacktestService()
    return _backtest_service


def reset_backtest_service() -> None:
    global _backtest_service
    _backtest_service = None


backtest_service = get_backtest_service()
