from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.ai_trader.service import AITraderService
from app.auth.dependencies import require_authenticated, require_permission
from app.auth.rbac import Permission
from app.core.responses import ok
from app.risk.models import AccountSnapshot
from app.trading.models import Candle

router = APIRouter(prefix="/api/ai-trader", tags=["ai-trader"])
service = AITraderService()


class AITraderSignalRequest(BaseModel):
    symbol: str = "XAUUSD"
    timeframe: str = "M5"
    candles: list[Candle] = Field(min_length=1)
    min_confidence: float = Field(default=0.55, ge=0.0, le=1.0)


class AITraderPaperRequest(AITraderSignalRequest):
    snapshot: AccountSnapshot | None = None


@router.get("/status")
def ai_trader_status(_: object = Depends(require_authenticated)) -> dict[str, Any]:
    return ok(
        {
            "enabled": False,
            "dry_run": True,
            "simulation_only": True,
            "model_version": service.model_version,
            "safety_notice": "Simulation only. Not financial advice. Dry-run only.",
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
    )
    return ok(
        {
            "signal": decision["signal"].model_dump(mode="json"),
            "validation": decision["validation"].model_dump(mode="json"),
            "feature_summary": decision["feature_summary"],
            "model_version": decision["model_version"],
            "simulation_only": True,
            "safety_notice": decision["safety_notice"],
        }
    )


@router.post("/paper-" "trade")
def run_ai_trader_paper_simulation(
    req: AITraderPaperRequest,
    _: object = Depends(require_permission(Permission.RUN_DRY_RUN_TRADING)),
) -> dict[str, Any]:
    result = service.paper_trade(
        candles=req.candles,
        symbol=req.symbol,
        timeframe=req.timeframe,
        min_confidence=req.min_confidence,
        snapshot=req.snapshot,
    )
    return ok(
        {
            "signal": result["signal"].model_dump(mode="json"),
            "validation": result["validation"].model_dump(mode="json"),
            "feature_summary": result["feature_summary"],
            "model_version": result["model_version"],
            "simulation_only": True,
            "safety_notice": result["safety_notice"],
            "dry_run": True,
            "execution": result["execution"].model_dump(mode="json"),
        }
    )
