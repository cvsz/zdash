from __future__ import annotations

from typing import Any

from app.agents.base import AgentMessage, BaseAgent
from app.backtesting.backtest_service import BacktestService, get_backtest_service
from app.backtesting.models import BacktestRequest, OptimizationRequest
from app.core.events import event_bus


class JoeAgent(BaseAgent):
    def __init__(self, service: BacktestService | None = None) -> None:
        super().__init__(
            agent_id="joe",
            name="Nathan Cole",
            role="strategy_lab_coordinator",
            metadata={"tier": "rare", "legacy_name": "Joe"},
        )
        self._service = service or get_backtest_service()

    @property
    def service(self) -> BacktestService:
        return self._service

    def list_strategies(self) -> list[dict[str, Any]]:
        self._emit_received("list_strategies")
        self.status = "running"
        try:
            strategies = self.service.list_strategies()
            self.status = "idle"
            self._emit_completed("list_strategies", {"count": len(strategies)})
            return strategies
        except Exception as exc:
            self.status = "error"
            self._emit_failed("list_strategies", exc)
            raise

    def run_backtest(self, request: BacktestRequest):
        self._emit_received("run_backtest")
        self.status = "running"
        try:
            result = self.service.run_backtest(request)
            self.status = "idle"
            self._emit_completed(
                "run_backtest", {"result_id": result.id, "strategy": result.strategy}
            )
            return result
        except Exception as exc:
            self.status = "error"
            self._emit_failed("run_backtest", exc)
            raise

    def optimize(self, request: OptimizationRequest):
        self._emit_received("optimize")
        self.status = "running"
        try:
            result = self.service.optimize(request)
            self.status = "idle"
            self._emit_completed(
                "optimize",
                {
                    "result_id": result.id,
                    "executed_combinations": result.executed_combinations,
                    "total_combinations": result.total_combinations,
                },
            )
            return result
        except Exception as exc:
            self.status = "error"
            self._emit_failed("optimize", exc)
            raise

    def evaluate_promotion(self, result_id: str):
        self._emit_received("evaluate_promotion")
        self.status = "running"
        try:
            decision = self.service.evaluate_promotion(result_id)
            self.status = "idle"
            self._emit_completed(
                "evaluate_promotion",
                {
                    "result_id": result_id,
                    "approved": decision.approved,
                    "reason": decision.reason,
                },
            )
            return decision
        except Exception as exc:
            self.status = "error"
            self._emit_failed("evaluate_promotion", exc)
            raise

    def health_check(self):
        base = super().health_check()
        base["legacy_agent_id"] = self.id
        base["backtesting"] = self.service.get_status()
        return base

    def receive_message(self, message: AgentMessage):
        self._emit_received("receive_message", {"message": message.message})
        return self.run_task(task=message.message, context=message.context)

    def run_task(
        self, task: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        context = context or {}
        if task == "health":
            result = self.health_check()
        elif task == "list_strategies":
            result = {"strategies": self.list_strategies()}
        elif task == "run_backtest":
            backtest_request: BacktestRequest = BacktestRequest.model_validate(context.get("request", context))
            result = {"result": self.run_backtest(backtest_request).model_dump(mode="json")}
        elif task == "optimize":
            optimization_request: OptimizationRequest = OptimizationRequest.model_validate(
                context.get("request", context)
            )
            result = {"result": self.optimize(optimization_request).model_dump(mode="json")}
        elif task == "evaluate_promotion":
            result_id = str(context.get("result_id", "")).strip()
            if not result_id:
                raise ValueError("result_id is required")
            result = {
                "decision": self.evaluate_promotion(result_id).model_dump(mode="json")
            }
        else:
            raise ValueError(f"Unsupported Joe task: {task}")

        return {"task": task, "ok": True, **result}

    def _emit_received(
        self, command: str, payload: dict[str, Any] | None = None
    ) -> None:
        event_bus.emit(
            "joe.command.received",
            self.id,
            "Joe command received",
            {"command": command, **(payload or {})},
        )

    def _emit_completed(
        self, command: str, payload: dict[str, Any] | None = None
    ) -> None:
        event_bus.emit(
            "joe.command.completed",
            self.id,
            "Joe command completed",
            {"command": command, **(payload or {})},
        )

    def _emit_failed(self, command: str, exc: Exception) -> None:
        event_bus.emit(
            "joe.command.failed",
            self.id,
            "Joe command failed",
            {"command": command, "error": str(exc)},
        )
