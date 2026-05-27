from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.audit.audit_service import AuditService
from app.audit.models import AuditLogCreate
from app.auth.dependencies import require_authenticated, require_permission
from app.auth.models import AuthSession
from app.auth.rbac import Permission
from app.backtesting.backtest_service import get_backtest_service
from app.backtesting.models import BacktestRequest, OptimizationRequest
from app.backtesting.reports import BacktestReportBuilder
from app.core.responses import fail, ok
from app.db.session import get_db_session
from app.observability.metrics import metrics_store

router = APIRouter(prefix="/api/backtesting", tags=["backtesting"])
reports = BacktestReportBuilder()


def _actor_email(current_user: object) -> str:
    if isinstance(current_user, AuthSession):
        return current_user.username
    return "system"


def _maybe_audit(session: object, entry: AuditLogCreate) -> None:
    if isinstance(session, Session):
        AuditService(session).log(entry)


@router.get("/status")
def status(_: object = Depends(require_authenticated)):
    return ok(get_backtest_service().get_status())


@router.get("/strategies")
def strategies(_: object = Depends(require_authenticated)):
    return ok({"strategies": get_backtest_service().list_strategies()})


@router.post("/run")
def run(
    req: BacktestRequest,
    current_user: AuthSession = Depends(require_permission(Permission.RUN_BACKTESTS)),
    session: Session = Depends(get_db_session),
):
    try:
        result = get_backtest_service().run_backtest(req)
        metrics_store.increment_backtests()
        _maybe_audit(
            session,
            AuditLogCreate(
                actor_user_id="",
                actor_email=_actor_email(current_user),
                action="backtest.run",
                resource_type="backtest_result",
                resource_id=result.id,
                metadata={"strategy": result.strategy, "symbol": result.symbol},
            ),
        )
        return ok({"result": result.model_dump(mode="json")})
    except Exception as exc:
        return fail("BACKTEST_FAILED", str(exc))


@router.get("/results")
def results(_: object = Depends(require_authenticated)):
    return ok(
        {
            "results": [
                item.model_dump(mode="json")
                for item in get_backtest_service().get_results()
            ]
        }
    )


@router.get("/results/{result_id}")
def result(
    result_id: str,
    _: object = Depends(require_authenticated),
):
    item = get_backtest_service().get_result(result_id)
    if not item:
        return fail("RESULT_NOT_FOUND", "Backtest result not found")
    return ok({"result": item.model_dump(mode="json")})


@router.post("/optimize")
def optimize(
    req: OptimizationRequest,
    current_user: AuthSession = Depends(require_permission(Permission.RUN_BACKTESTS)),
    session: Session = Depends(get_db_session),
):
    try:
        optimization = get_backtest_service().optimize(req)
        metrics_store.increment_backtests()
        _maybe_audit(
            session,
            AuditLogCreate(
                actor_user_id="",
                actor_email=_actor_email(current_user),
                action="backtest.optimize",
                resource_type="optimization_result",
                resource_id=optimization.id,
                metadata={"strategy": optimization.request.strategy},
            ),
        )
        return ok({"optimization": optimization.model_dump(mode="json")})
    except Exception as exc:
        return fail("OPTIMIZER_FAILED", str(exc))


@router.get("/optimizations")
def optimizations(_: object = Depends(require_authenticated)):
    return ok(
        {
            "optimizations": [
                item.model_dump(mode="json")
                for item in get_backtest_service().get_optimization_results()
            ]
        }
    )


@router.post("/results/{result_id}/promotion-check")
def promotion(
    result_id: str,
    current_user: AuthSession = Depends(require_permission(Permission.RUN_BACKTESTS)),
    session: Session = Depends(get_db_session),
):
    try:
        decision = get_backtest_service().evaluate_promotion(result_id)
        _maybe_audit(
            session,
            AuditLogCreate(
                actor_user_id="",
                actor_email=_actor_email(current_user),
                action="backtest.promotion_check",
                resource_type="backtest_result",
                resource_id=result_id,
                metadata={"approved": decision.approved},
            ),
        )
        return ok({"decision": decision.model_dump(mode="json")})
    except Exception as exc:
        return fail("PROMOTION_CHECK_FAILED", str(exc))


@router.get("/results/{result_id}/report")
def report(
    result_id: str,
    _: object = Depends(require_authenticated),
):
    item = get_backtest_service().get_result(result_id)
    if not item:
        return fail("RESULT_NOT_FOUND", "Backtest result not found")
    return ok(
        {
            "markdown_report": reports.build_markdown_report(item),
            "summary": reports.build_summary(item),
        }
    )
