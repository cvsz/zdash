from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.ai_trader.service import (
    AITraderService,
    MODEL_VERSION,
    RISK_POLICY,
    SAFETY_NOTICE,
)
from app.auth.dependencies import require_permission
from app.auth.rbac import Permission
from app.core.responses import ok
from app.risk.models import AccountSnapshot
from app.trading.models import Candle

router = APIRouter(prefix="/api/ai-trader", tags=["ai-trader"])
service = AITraderService()


class AITraderSignalRequest(BaseModel):
    symbol: str = "XAUUSD"
    timeframe: str = "M5"
    strategy_id: str = "trend_momentum_v1"
    candles: list[Candle] = Field(default_factory=list)
    min_confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class AITraderCompareRequest(BaseModel):
    symbol: str = "XAUUSD"
    timeframe: str = "M5"
    candles: list[Candle] = Field(default_factory=list)
    strategy_ids: list[str] = Field(default_factory=list)


class AITraderPaperRequest(AITraderSignalRequest):
    snapshot: AccountSnapshot | None = None


def _decision_payload(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "signal": decision["signal"].model_dump(mode="json"),
        "validation": decision["validation"].model_dump(mode="json"),
        "features": decision.get("features", {}),
        "feature_summary": decision.get("feature_summary", {}),
        "warnings": decision.get("warnings", []),
        "explanation": decision.get("explanation", ""),
        "model_version": decision["model_version"],
        "simulation_only": True,
        "safety_notice": decision["safety_notice"],
        "risk_policy": decision.get("risk_policy", dict(RISK_POLICY)),
    }


@router.get("/status")
def ai_trader_status(
    _: object = Depends(require_permission(Permission.READ_TRADING_SIGNALS)),
) -> dict[str, Any]:
    return ok(
        {
            "enabled": True,
            "simulation_only": True,
            "live_execution_allowed": False,
            "dry_run_forced": True,
            "model_version": MODEL_VERSION,
            "strategies": [
                strategy.as_dict() for strategy in service.list_strategies()
            ],
            "safety_policy": dict(RISK_POLICY),
            "safety_notice": SAFETY_NOTICE,
        }
    )


@router.get("/strategies")
def list_ai_trader_strategies(
    _: object = Depends(require_permission(Permission.READ_TRADING_SIGNALS)),
) -> dict[str, Any]:
    return ok(
        {
            "strategies": [
                strategy.as_dict() for strategy in service.list_strategies()
            ],
            "simulation_only": True,
            "model_version": MODEL_VERSION,
            "safety_notice": SAFETY_NOTICE,
        }
    )


@router.post("/signal")
def generate_ai_trader_signal(
    req: AITraderSignalRequest,
    _: object = Depends(require_permission(Permission.READ_TRADING_SIGNALS)),
) -> dict[str, Any]:
    decision = service.generate_decision(
        candles=req.candles,
        symbol=req.symbol,
        timeframe=req.timeframe,
        min_confidence=req.min_confidence,
        strategy_id=req.strategy_id,
    )
    return ok(_decision_payload(decision))


@router.post("/compare")
def compare_ai_trader_strategies(
    req: AITraderCompareRequest,
    _: object = Depends(require_permission(Permission.READ_TRADING_SIGNALS)),
) -> dict[str, Any]:
    compared = service.compare_strategies(
        candles=req.candles,
        symbol=req.symbol,
        timeframe=req.timeframe,
        strategy_ids=req.strategy_ids or None,
    )
    return ok(
        {
            "ranked_decisions": [
                _decision_payload(decision) for decision in compared["ranked_decisions"]
            ],
            "model_version": compared["model_version"],
            "simulation_only": True,
            "safety_notice": compared["safety_notice"],
        }
    )


@router.post("/paper-trade")
def run_ai_trader_paper_simulation(
    req: AITraderPaperRequest,
    _: object = Depends(require_permission(Permission.RUN_DRY_RUN_TRADING)),
) -> dict[str, Any]:
    result = service.paper_trade(
        candles=req.candles,
        symbol=req.symbol,
        timeframe=req.timeframe,
        min_confidence=req.min_confidence,
        strategy_id=req.strategy_id,
        snapshot=req.snapshot,
    )
    payload = _decision_payload(result)
    payload.update(
        {
            "dry_run": True,
            "live_execution_allowed": False,
            "execution": result["execution"].model_dump(mode="json"),
        }
    )
    return ok(payload)
