def run_task(task):
    if task.task_type in {
        "content_publish_dry_run",
        "iot_status_check",
        "trading_scan",
        "risk_check",
        "backtest_run",
        "custom",
    }:
        return {"ok": True, "task_type": task.task_type, "dry_run": True}
    return {"ok": True}
