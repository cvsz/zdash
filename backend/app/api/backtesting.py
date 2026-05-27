from __future__ import annotations

from fastapi import APIRouter

from app.backtesting.backtest_service import get_backtest_service
from app.backtesting.models import BacktestRequest, OptimizationRequest
from app.backtesting.reports import BacktestReportBuilder
from app.core.responses import fail, ok

router = APIRouter(prefix="/api/backtesting", tags=["backtesting"])
reports = BacktestReportBuilder()


@router.get("/status")
def status():
    return ok(get_backtest_service().get_status())


@router.get("/strategies")
def strategies():
    return ok({"strategies": get_backtest_service().list_strategies()})


@router.post("/run")
def run(req: BacktestRequest):
    try:
        result = get_backtest_service().run_backtest(req)
        return ok({"result": result.model_dump(mode="json")})
    except Exception as exc:
        return fail("BACKTEST_FAILED", str(exc))


@router.get("/results")
def results():
    return ok(
        {
            "results": [
                item.model_dump(mode="json")
                for item in get_backtest_service().get_results()
            ]
        }
    )


@router.get("/results/{result_id}")
def result(result_id: str):
    item = get_backtest_service().get_result(result_id)
    if not item:
        return fail("RESULT_NOT_FOUND", "Backtest result not found")
    return ok({"result": item.model_dump(mode="json")})


@router.post("/optimize")
def optimize(req: OptimizationRequest):
    try:
        optimization = get_backtest_service().optimize(req)
        return ok({"optimization": optimization.model_dump(mode="json")})
    except Exception as exc:
        return fail("OPTIMIZER_FAILED", str(exc))


@router.get("/optimizations")
def optimizations():
    return ok(
        {
            "optimizations": [
                item.model_dump(mode="json")
                for item in get_backtest_service().get_optimization_results()
            ]
        }
    )


@router.post("/results/{result_id}/promotion-check")
def promotion(result_id: str):
    try:
        decision = get_backtest_service().evaluate_promotion(result_id)
        return ok({"decision": decision.model_dump(mode="json")})
    except Exception as exc:
        return fail("PROMOTION_CHECK_FAILED", str(exc))


@router.get("/results/{result_id}/report")
def report(result_id: str):
    item = get_backtest_service().get_result(result_id)
    if not item:
        return fail("RESULT_NOT_FOUND", "Backtest result not found")
    return ok(
        {
            "markdown_report": reports.build_markdown_report(item),
            "summary": reports.build_summary(item),
        }
    )
