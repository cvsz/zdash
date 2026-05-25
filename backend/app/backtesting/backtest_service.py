from __future__ import annotations

from app.backtesting.models import BacktestRequest, BacktestResult, OptimizationRequest, OptimizationResult
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
        s = get_settings()
        return {"enabled": s.backtesting_enabled, "available_strategies": self.list_strategies(), "stored_result_count": len(self.results), "stored_optimization_count": len(self.optimization_results), "primary_strategy_candidate": s.primary_strategy, "promotion_enabled": s.allow_strategy_promotion}

    def list_strategies(self): return self.lab.list_strategies()
    def run_backtest(self, request: BacktestRequest) -> BacktestResult:
        event_bus.emit("backtest.started", "backtest_service", "Backtest started", {"strategy": request.strategy})
        try:
            r = self.lab.run_backtest(request); self.results.insert(0, r)
            event_bus.emit("backtest.completed", "backtest_service", "Backtest completed", {"result_id": r.id}); return r
        except Exception as e:
            event_bus.emit("backtest.failed", "backtest_service", "Backtest failed", {"error": str(e)}); raise
    def get_results(self): return self.results
    def get_result(self, result_id: str): return next((r for r in self.results if r.id == result_id), None)
    def optimize(self, request: OptimizationRequest) -> OptimizationResult:
        event_bus.emit("optimizer.started", "backtest_service", "Optimization started", {"strategy": request.strategy})
        try:
            r = self.optimizer.optimize(request); self.optimization_results.insert(0, r)
            event_bus.emit("optimizer.completed", "backtest_service", "Optimization completed", {"result_id": r.id}); return r
        except Exception as e:
            event_bus.emit("optimizer.failed", "backtest_service", "Optimization failed", {"error": str(e)}); raise
    def get_optimization_results(self): return self.optimization_results
    def evaluate_promotion(self, result_id: str):
        result = self.get_result(result_id)
        if result is None: raise ValueError("Result not found")
        decision = self.promotion_gate.evaluate(result)
        event_bus.emit("strategy.promotion.evaluated", "backtest_service", "Promotion evaluated", {"result_id": result_id, "approved": decision.approved})
        event_bus.emit("strategy.promotion.approved" if decision.approved else "strategy.promotion.rejected", "backtest_service", "Promotion decision", {"result_id": result_id})
        return decision


backtest_service = BacktestService()
