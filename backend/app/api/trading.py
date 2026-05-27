from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.responses import ok
from app.trading.models import ExecutionRequest, TradingSignal
from app.trading.trading_service import TradingService

router = APIRouter(prefix="/api/trading", tags=["trading"])

service = TradingService()


class ScanRequest(BaseModel):
    symbol: str = "XAUUSD"
    timeframe: str = "M5"


@router.get("/status")
def trading_status() -> dict:
    return ok(service.get_status())


@router.post("/scan")
def scan(req: ScanRequest) -> dict:
    result = service.scan_xau(symbol=req.symbol, timeframe=req.timeframe)
    return ok(result.model_dump(mode="json"))


@router.post("/validate-signal")
def validate_signal(signal: TradingSignal) -> dict:
    validation = service.validate_signal(signal)
    return ok(validation.model_dump(mode="json"))


@router.post("/dry-run-execute")
def dry_run_execute(req: ExecutionRequest) -> dict:
    dry_run_request = req.model_copy(update={"dry_run": True, "confirmation": False})
    result = service.execution_engine.execute(dry_run_request)
    return ok(result.model_dump(mode="json"))


# Backward-compatible alias used by older clients.
@router.post("/dry-run")
def dry_run_execute_legacy(req: ExecutionRequest) -> dict:
    return dry_run_execute(req)
