from __future__ import annotations

from app.backtesting.backtest_service import get_backtest_service
from app.backtesting.models import BacktestRequest
from app.content.pipeline import get_content_pipeline
from app.core.config import get_settings
from app.notifications.notification_service import get_notification_service
from app.risk.guardian_service import get_guardian_service
from app.risk.models import AccountSnapshot


def run_task(task) -> dict:
    settings = get_settings()
    task_type = task.task_type
    payload = task.payload or {}

    if task_type == "risk_check":
        snapshot = AccountSnapshot(
            balance=float(payload.get("balance", 10000)),
            equity=float(payload.get("equity", 10000)),
            peak_equity=float(payload.get("peak_equity", 10000)),
            daily_start_equity=float(payload.get("daily_start_equity", 10000)),
            open_positions=int(payload.get("open_positions", 0)),
            floating_pnl=float(payload.get("floating_pnl", 0)),
            realized_pnl_today=float(payload.get("realized_pnl_today", 0)),
        )
        decision = get_guardian_service().check(snapshot)
        return {"ok": True, "task_type": task_type, "decision": decision.model_dump()}

    if task_type == "backtest_run":
        request = BacktestRequest(
            strategy=str(payload.get("strategy", settings.primary_strategy)),
            symbol=str(payload.get("symbol", settings.backtest_default_symbol)),
            timeframe=str(payload.get("timeframe", settings.backtest_default_timeframe)),
            dataset=str(payload.get("dataset", "")),
            initial_balance=float(payload.get("initial_balance", settings.backtest_initial_balance)),
            risk_per_trade_percent=float(
                payload.get(
                    "risk_per_trade_percent",
                    settings.backtest_default_risk_per_trade_percent,
                )
            ),
        )
        result = get_backtest_service().run_backtest(request)
        return {"ok": True, "task_type": task_type, "result_id": result.id}

    if task_type == "optimization_run":
        return {
            "ok": True,
            "task_type": task_type,
            "note": "optimization dispatch not wired for automatic runs",
            "dry_run": True,
        }

    if task_type == "content_pipeline_run":
        from app.content.models import CreateContentRequest
        topic = str(payload.get("topic", "Educational simulation market update"))
        pipeline_result = get_content_pipeline().run_full_pipeline(CreateContentRequest(topic=topic))
        return {"ok": True, "task_type": task_type, "run_id": pipeline_result.id}

    if task_type == "content_publish_dry_run":
        return {
            "ok": True,
            "task_type": task_type,
            "published": False,
            "dry_run": True,
            "note": "Publishing remains approval-gated",
        }

    if task_type == "iot_status_check":
        return {
            "ok": True,
            "task_type": task_type,
            "dry_run": settings.iot_dry_run,
            "real_actions_approved": settings.iot_real_actions_approved,
            "status": "simulated",
        }

    if task_type == "notification_dispatch":
        service = get_notification_service()
        notification = service.send_test_notification(
            organization_id=task.organization_id,
            workspace_id=task.workspace_id,
            actor_user_id=str(payload.get("actor_user_id", "worker")),
            title=str(payload.get("title", "Worker notification")),
            message=str(payload.get("message", "Dry-run notification dispatch")),
        )
        return {"ok": True, "task_type": task_type, "notification": notification}

    if task_type in {"trading_scan", "audit_compaction", "backup_run", "custom"}:
        return {
            "ok": True,
            "task_type": task_type,
            "dry_run": True,
            "payload": payload,
        }

    return {"ok": False, "task_type": task_type, "error": "unsupported task type"}
