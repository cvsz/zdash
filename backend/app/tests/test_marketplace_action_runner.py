from __future__ import annotations

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.marketplace.builtins import BUILTINS
from app.marketplace.models import (
    PluginActionRun,
    PluginActionResult,
    PluginInstallation,
)
from app.marketplace.plugin_registry import seed_builtins
from app.marketplace.plugin_runtime import run_action


def _memory_session() -> Session:
    engine = create_engine("sqlite://", future=True)
    Base.metadata.create_all(bind=engine)
    return Session(engine)


def _get_plugin_id_by_slug(slug: str) -> str:
    for p in BUILTINS:
        if p.slug == slug:
            return p.id
    raise ValueError(f"Builtin not found: {slug}")


def test_action_risk_summary():
    db = _memory_session()
    seed_builtins(db)
    plugin_id = _get_plugin_id_by_slug("zdash-risk-summary")
    result = run_action(db, plugin_id, "summarize", {})
    assert isinstance(result, PluginActionResult)
    assert result.ok is True
    assert result.dry_run is True
    assert "total_drawdown_pct" in result.output
    assert result.output["total_drawdown_pct"] == -12.4
    assert "guardian_status" in result.output
    assert result.output["halt_engaged"] is False


def test_action_backtest_report():
    db = _memory_session()
    seed_builtins(db)
    plugin_id = _get_plugin_id_by_slug("zdash-backtest-reporter")
    result = run_action(db, plugin_id, "report", {"strategy": "test_strat"})
    assert result.ok is True
    assert result.output["strategy"] == "test_strat"
    assert result.output["symbol"] == "XAUUSD"
    assert result.output["total_trades"] == 127
    assert result.output["win_rate_pct"] == 58.3


def test_action_content_calendar():
    db = _memory_session()
    seed_builtins(db)
    plugin_id = _get_plugin_id_by_slug("zdash-content-calendar")
    result = run_action(db, plugin_id, "list", {})
    assert result.ok is True
    assert "scheduled_items" in result.output
    assert result.output["total_scheduled"] == 2


def test_action_scheduler_health():
    db = _memory_session()
    seed_builtins(db)
    plugin_id = _get_plugin_id_by_slug("zdash-scheduler-health")
    result = run_action(db, plugin_id, "check", {})
    assert result.ok is True
    assert "jobs" in result.output
    assert result.output["total_jobs"] == 3
    assert result.output["healthy"] == 2


def test_action_alert_router():
    db = _memory_session()
    seed_builtins(db)
    plugin_id = _get_plugin_id_by_slug("zdash-alert-router")
    result = run_action(
        db,
        plugin_id,
        "route",
        {"severity": "critical", "source": "test", "message": "test alert"},
    )
    assert result.ok is True
    assert result.output["received"]["severity"] == "critical"
    assert "slack" in result.output["routing_decision"]["channels"]


def test_action_alert_router_info():
    db = _memory_session()
    seed_builtins(db)
    plugin_id = _get_plugin_id_by_slug("zdash-alert-router")
    result = run_action(
        db,
        plugin_id,
        "route",
        {"severity": "info", "source": "test", "message": "info alert"},
    )
    assert result.ok is True
    assert result.output["routing_decision"]["channels"] == ["slack"]


def test_action_tenant_audit_export():
    db = _memory_session()
    seed_builtins(db)
    plugin_id = _get_plugin_id_by_slug("zdash-tenant-audit-export")
    result = run_action(
        db, plugin_id, "export", {"tenant_id": "tenant-1", "export_type": "csv"}
    )
    assert result.ok is True
    assert result.output["tenant_id"] == "tenant-1"
    assert result.output["dry_run"] is True
    assert "secrets_included" in result.output
    assert result.output["secrets_included"] is False


def test_action_unknown_entrypoint():
    db = _memory_session()
    seed_builtins(db)
    result = run_action(db, "nonexistent-id", "test", {})
    assert result.ok is False
    assert "not found" in result.message


def test_action_always_dry_run():
    db = _memory_session()
    seed_builtins(db)
    plugin_id = _get_plugin_id_by_slug("zdash-risk-summary")
    result = run_action(db, plugin_id, "summarize", {}, dry_run=False)
    assert result.dry_run is True
    assert result.ok is True


def test_action_logs_run_to_db():
    db = _memory_session()
    Base.metadata.create_all(bind=db.bind)
    seed_builtins(db)
    plugin_id = _get_plugin_id_by_slug("zdash-risk-summary")

    installation = PluginInstallation(
        id="test-installation-action-log",
        organization_id="test-org",
        workspace_id="test-ws",
        plugin_id=plugin_id,
        version="1.0.0",
        status="enabled",
        config_json={},
        enabled=True,
        installed_by="test",
    )
    db.add(installation)
    db.commit()

    result = run_action(
        db,
        plugin_id,
        "summarize",
        {},
        installation_id=installation.id,
    )
    assert result.ok is True

    runs = (
        db.query(PluginActionRun)
        .filter(PluginActionRun.installation_id == installation.id)
        .all()
    )
    assert len(runs) == 1
    assert runs[0].installation_id == installation.id
    assert runs[0].action == "summarize"
    assert runs[0].dry_run is True
    assert runs[0].status == "dry_run"


def test_action_result_timestamp_utc():
    db = _memory_session()
    seed_builtins(db)
    plugin_id = _get_plugin_id_by_slug("zdash-risk-summary")
    result = run_action(db, plugin_id, "summarize", {})
    assert isinstance(result.timestamp, datetime)
    assert result.timestamp.tzinfo is not None
