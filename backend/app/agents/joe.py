from app.agents.base import BaseAgent
from app.backtesting.backtest_service import backtest_service
from app.backtesting.models import BacktestRequest, OptimizationRequest
from app.core.events import event_bus


class JoeAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            agent_id="joe",
            name="Nathan Cole",
            role="analyst_developer",
            metadata={"tier": "rare", "legacy_name": "Joe"},
        )

    def list_strategies(self):
        event_bus.emit("joe.command.received", "joe", "list_strategies")
        data = backtest_service.list_strategies()
        event_bus.emit("joe.command.completed", "joe", "list_strategies")
        return data

    def run_backtest(self, request: BacktestRequest):
        event_bus.emit("joe.command.received", "joe", "run_backtest")
        try:
            out = backtest_service.run_backtest(request)
            event_bus.emit("joe.command.completed", "joe", "run_backtest")
            return out
        except Exception:
            event_bus.emit("joe.command.failed", "joe", "run_backtest")
            raise

    def optimize(self, request: OptimizationRequest):
        event_bus.emit("joe.command.received", "joe", "optimize")
        try:
            out = backtest_service.optimize(request)
            event_bus.emit("joe.command.completed", "joe", "optimize")
            return out
        except Exception:
            event_bus.emit("joe.command.failed", "joe", "optimize")
            raise

    def evaluate_promotion(self, result_id: str):
        event_bus.emit("joe.command.received", "joe", "evaluate_promotion")
        out = backtest_service.evaluate_promotion(result_id)
        event_bus.emit("joe.command.completed", "joe", "evaluate_promotion")
        return out

    def health_check(self):
        base = super().health_check()
        base["legacy_agent_id"] = self.id
        return base

    def receive_message(self, message):
        return {"response_text": "Nathan Cole received message", "message": message.message}

    def run_task(self, task, context=None):
        return {"task": task, "status": "accepted", "context": context or {}}
