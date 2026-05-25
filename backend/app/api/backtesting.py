from fastapi import APIRouter

from app.backtesting.backtest_service import backtest_service
from app.backtesting.models import BacktestRequest, OptimizationRequest
from app.backtesting.reports import BacktestReportBuilder
from app.core.responses import fail, ok

router = APIRouter(prefix="/api/backtesting", tags=["backtesting"])
reports = BacktestReportBuilder()


@router.get("/status")
def status():
    return ok(backtest_service.get_status())


@router.get("/strategies")
def strategies():
    return ok(backtest_service.list_strategies())


@router.post("/run")
def run(req: BacktestRequest):
    try:
        return ok(backtest_service.run_backtest(req).model_dump())
    except Exception as e:
        return fail("BACKTEST_FAILED", str(e))


@router.get("/results")
def results():
    return ok([x.model_dump() for x in backtest_service.get_results()])


@router.get("/results/{result_id}")
def result(result_id: str):
    r = backtest_service.get_result(result_id)
    if not r:
        return fail("RESULT_NOT_FOUND", "Backtest result not found")
    return ok(r.model_dump())


@router.post("/optimize")
def optimize(req: OptimizationRequest):
    try:
        return ok(backtest_service.optimize(req).model_dump())
    except Exception as e:
        return fail("OPTIMIZER_FAILED", str(e))


@router.get("/optimizations")
def optimizations():
    return ok([x.model_dump() for x in backtest_service.get_optimization_results()])


@router.post("/results/{result_id}/promotion-check")
def promotion(result_id: str):
    try:
        return ok(backtest_service.evaluate_promotion(result_id).model_dump())
    except Exception as e:
        return fail("PROMOTION_CHECK_FAILED", str(e))


@router.get("/results/{result_id}/report")
def report(result_id: str):
    r = backtest_service.get_result(result_id)
    if not r:
        return fail("RESULT_NOT_FOUND", "Backtest result not found")
    return ok({"markdown_report": reports.build_markdown_report(r), "summary": reports.build_summary(r)})
