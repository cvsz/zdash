from app.backtesting.backtest_service import get_backtest_service
from app.core.events import event_bus
from app.scheduler.scheduler_service import get_scheduler_service


def _find_job_id_by_name(name: str) -> str:
    scheduler = get_scheduler_service()
    for job in scheduler.list_jobs():
        if job.name == name:
            return job.id
    raise AssertionError(f"Missing scheduler job: {name}")


def test_scheduler_backtest_job_calls_backtest_service() -> None:
    scheduler = get_scheduler_service()
    backtest_job_id = _find_job_id_by_name("backtest")

    service = get_backtest_service()
    assert len(service.get_results()) == 0

    result = scheduler.run_job(backtest_job_id, manual=True)
    assert result.ok is True
    assert result.status == "completed"
    assert result.output["job_type"] == "backtest"
    assert "result_id" in result.output
    assert len(service.get_results()) == 1


def test_scheduler_backtest_job_returns_result_summary() -> None:
    scheduler = get_scheduler_service()
    backtest_job_id = _find_job_id_by_name("backtest")

    result = scheduler.run_job(backtest_job_id, manual=True)
    assert "total_trades" in result.output
    assert "net_profit_percent" in result.output
    assert "max_drawdown_percent" in result.output


def test_scheduler_does_not_promote_strategy_automatically() -> None:
    scheduler = get_scheduler_service()
    backtest_job_id = _find_job_id_by_name("backtest")
    event_bus.clear()

    result = scheduler.run_job(backtest_job_id, manual=True)
    assert result.ok is True
    assert result.output["promotion_auto_run"] is False

    event_types = {event.type for event in event_bus.list_events(limit=200)}
    assert "strategy.promotion.approved" not in event_types
    assert "strategy.promotion.rejected" not in event_types
