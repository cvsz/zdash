"""Safe built-in plugin action runners.

All actions default to dry-run mode and never produce
side effects on external systems.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from .models import PluginActionRun, PluginActionResult
from .plugin_registry import get_plugin


def run_action(
    db: Session,
    plugin_id: str,
    action: str,
    payload: dict[str, Any] | None = None,
    dry_run: bool = True,
    installation_id: str | None = None,
) -> PluginActionResult:
    """Execute a plugin action safely.

    Parameters
    ----------
    db :
        Active SQLAlchemy session.
    plugin_id :
        Primary key of the PluginManifest to run.
    action :
        Action name (e.g. ``"summarize"``, ``"report"``).
    payload :
        Optional action-specific input data.
    dry_run :
        When True (default) no real-world side effects occur.

    Returns
    -------
    PluginActionResult
        Always includes ``dry_run=True`` regardless of input.
    """
    payload = payload or {}
    manifest = get_plugin(db, plugin_id)
    if not manifest:
        return PluginActionResult(
            plugin_id=plugin_id,
            action=action,
            ok=False,
            message=f"plugin {plugin_id} not found",
            output={},
            dry_run=True,
            timestamp=datetime.now(timezone.utc),
        )

    entrypoint = getattr(manifest, "entrypoint", "") or ""
    output: dict[str, Any] = {}

    if entrypoint == "builtin://risk-summary":
        output = _risk_summary(payload)
    elif entrypoint == "builtin://backtest-reporter":
        output = _backtest_report(payload)
    elif entrypoint == "builtin://content-calendar":
        output = _content_calendar(payload)
    elif entrypoint == "builtin://scheduler-health":
        output = _scheduler_health(payload)
    elif entrypoint == "builtin://alert-router":
        output = _simulate_alert_route(payload)
    elif entrypoint == "builtin://tenant-audit-export":
        output = _audit_export_metadata(payload)
    else:
        return PluginActionResult(
            plugin_id=plugin_id,
            action=action,
            ok=False,
            message=f"unknown entrypoint: {entrypoint}",
            output={},
            dry_run=True,
            timestamp=datetime.now(timezone.utc),
        )

    if installation_id:
        _log_run(db, installation_id, action, payload, dry_run, output)

    return PluginActionResult(
        plugin_id=plugin_id,
        action=action,
        ok=True,
        message="dry-run completed",
        output=output,
        dry_run=True,
        timestamp=datetime.now(timezone.utc),
    )


# ------------------------------------------------------------------ #
# Built-in action implementations (all read-only / mock)                #
# ------------------------------------------------------------------ #


def _risk_summary(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "total_drawdown_pct": -12.4,
        "current_drawdown_pct": -3.7,
        "peak_to_current_pct": -3.7,
        "volatility_annualized_pct": 18.2,
        "var_95_pct": -2.1,
        "concentration_pct": {
            "strategy_a": 45.0,
            "strategy_b": 30.0,
            "strategy_c": 25.0,
        },
        "guardian_status": "active",
        "halt_engaged": False,
    }


def _backtest_report(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "strategy": payload.get("strategy", "default"),
        "symbol": payload.get("symbol", "XAUUSD"),
        "timeframe": payload.get("timeframe", "H1"),
        "total_trades": 127,
        "win_rate_pct": 58.3,
        "profit_factor": 1.42,
        "net_profit": 3420.50,
        "max_drawdown_pct": -8.1,
        "sharpe_ratio": 1.21,
        "calmar_ratio": 0.85,
        "trades": [
            {
                "entry": "2025-01-15T08:00:00Z",
                "exit": "2025-01-15T16:00:00Z",
                "pnl": 120.0,
            },
            {
                "entry": "2025-01-16T09:30:00Z",
                "exit": "2025-01-16T14:15:00Z",
                "pnl": -45.0,
            },
        ],
    }


def _content_calendar(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "scheduled_items": [
            {
                "id": "c01",
                "title": "Market Update",
                "channel": "twitter",
                "scheduled_at": "2026-06-01T14:00:00Z",
                "status": "approved",
            },
            {
                "id": "c02",
                "title": "Weekly Report",
                "channel": "linkedin",
                "scheduled_at": "2026-06-03T09:00:00Z",
                "status": "draft",
            },
        ],
        "total_scheduled": 2,
        "pending_approval": 0,
    }


def _scheduler_health(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "jobs": [
            {
                "name": "risk-snapshot",
                "last_run": "2026-05-31T12:00:00Z",
                "status": "success",
                "success_rate_pct": 99.2,
            },
            {
                "name": "backtest-daily",
                "last_run": "2026-05-31T06:00:00Z",
                "status": "success",
                "success_rate_pct": 97.8,
            },
            {
                "name": "content-publish",
                "last_run": "2026-05-30T08:00:00Z",
                "status": "failed",
                "success_rate_pct": 85.0,
            },
        ],
        "total_jobs": 3,
        "healthy": 2,
        "unhealthy": 1,
    }


def _simulate_alert_route(payload: dict[str, Any]) -> dict[str, Any]:
    severity = payload.get("severity", "info")
    source = payload.get("source", "unknown")
    return {
        "received": {
            "severity": severity,
            "source": source,
            "message": payload.get("message", ""),
        },
        "routing_decision": {
            "channels": _alert_channels(severity),
            "reason": f"routed by severity={severity}",
        },
        "simulated": True,
    }


def _alert_channels(severity: str) -> list[str]:
    mapping = {
        "critical": ["slack", "email", "webhook"],
        "warning": ["slack", "email"],
        "info": ["slack"],
    }
    return mapping.get(severity, ["log"])


def _audit_export_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    tenant = payload.get("tenant_id", "unknown")
    return {
        "tenant_id": tenant,
        "export_type": payload.get("export_type", "csv"),
        "record_count_estimate": 1250,
        "date_range": {
            "from": payload.get("from", "2026-01-01"),
            "to": payload.get("to", "2026-05-31"),
        },
        "columns": [
            "timestamp",
            "actor_email",
            "action",
            "resource_type",
            "resource_id",
            "result",
            "ip_address",
        ],
        "dry_run": True,
        "message": "Run with dry_run=False (and admin permission) to "
        "generate the actual export file. "
        "No secrets are included in export metadata.",
        "secrets_included": False,
    }


# ------------------------------------------------------------------ #
# Audit logging                                                        #
# ------------------------------------------------------------------ #


def _log_run(
    db: Session,
    installation_id: str,
    action: str,
    payload: dict[str, Any],
    dry_run: bool,
    output: dict[str, Any],
) -> None:
    """Persist a PluginActionRun record for audit purposes."""
    run = PluginActionRun(
        installation_id=installation_id,
        action=action,
        payload_json=payload,
        dry_run=dry_run,
        status="dry_run" if dry_run else "completed",
        output_json=output,
        error=None,
    )
    db.add(run)
    db.commit()
