# mypy: ignore-errors
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.audit_service import AuditService
from app.audit.models import AuditLogCreate
from app.billing.entitlement_service import check_feature
from app.billing.quota_service import consume
from app.core.events import event_bus
from app.db.repositories import MarketplaceRepository
from app.db.session import SessionLocal
from app.marketplace.models import (
    PluginInstallStatus,
    PluginInstallation,
    PluginManifest,
    PluginStatus,
    manifest_to_dict,
)
from app.marketplace.plugin_registry import (
    list_plugins as registry_list_plugins,
    seed_builtins,
)
from app.marketplace.plugin_runtime import run_action
from app.marketplace.safety import check_plugin_action

SECRET_KEYS = {"secret", "password", "token", "key", "credential"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _session(db: Session | None) -> tuple[Session, bool]:
    if db is not None:
        return db, False
    return SessionLocal(), True


def _redact_secrets(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return payload

    redacted: dict[str, Any] = {}
    for key, value in payload.items():
        if any(secret_key in key.lower() for secret_key in SECRET_KEYS):
            redacted[key] = "***REDACTED***"
        elif isinstance(value, dict):
            redacted[key] = _redact_secrets(value)
        else:
            redacted[key] = value
    return redacted


def validate_install(
    organization_id: str,
    plugin_id: str,
    workspace_id: str,
    config: dict[str, Any] | None = None,
    db: Session | None = None,
) -> dict[str, Any]:
    session, own_session = _session(db)
    if own_session:
        seed_builtins(session)

    try:
        manifest = session.execute(
            select(PluginManifest).where(PluginManifest.id == plugin_id)
        ).scalar_one_or_none()

        if not manifest:
            return {"ok": False, "error": "PLUGIN_NOT_FOUND"}

        if manifest.status != PluginStatus.approved.value:
            return {"ok": False, "error": "PLUGIN_NOT_APPROVED"}

        repo = MarketplaceRepository(session)
        for inst in repo.list_installations(organization_id, workspace_id):
            if inst.plugin_id == plugin_id and inst.status not in (
                PluginInstallStatus.removed.value,
                PluginInstallStatus.failed.value,
            ):
                return {"ok": False, "error": "ALREADY_INSTALLED"}

        ent = check_feature(organization_id, "feature.marketplace")
        if not ent.allowed:
            return {"ok": False, "error": "FEATURE_NOT_ENTITLED"}

        quota = consume(organization_id, workspace_id, "marketplace_plugins")
        if not quota.allowed:
            return {"ok": False, "error": "QUOTA_EXCEEDED"}

        return {"ok": True, "manifest": manifest, "config": config or {}}
    finally:
        if own_session:
            session.close()


def list_installations(
    organization_id: str,
    workspace_id: str | None = None,
) -> list[PluginInstallation]:
    with SessionLocal() as session:
        repo = MarketplaceRepository(session)
        return repo.list_installations(organization_id, workspace_id)


def install_plugin(
    organization_id: str,
    plugin_id: str,
    workspace_id: str,
    config: dict[str, Any] | None = None,
    installed_by: str = "system",
    db: Session | None = None,
) -> dict[str, Any]:
    validation = validate_install(
        organization_id,
        plugin_id,
        workspace_id,
        config,
        db=db,
    )
    if not validation.get("ok"):
        return validation

    session, own_session = _session(db)
    try:
        repo = MarketplaceRepository(session)
        audit = AuditService(session)

        inst = repo.create_installation(
            organization_id=organization_id,
            workspace_id=workspace_id,
            plugin_id=plugin_id,
            version="1.0.0",
            status=PluginInstallStatus.installed.value,
            config_json=config or {},
            enabled=False,
            installed_by=installed_by,
        )

        safe_config = _redact_secrets(config or {})
        event_bus.emit(
            "marketplace.plugin.installed",
            "plugin_service",
            f"Plugin {plugin_id} installed",
            {
                "plugin_id": plugin_id,
                "installation_id": inst.id,
                "organization_id": organization_id,
                "workspace_id": workspace_id,
                "config": safe_config,
            },
        )

        audit.log(
            AuditLogCreate(
                actor_user_id=installed_by,
                actor_email="",
                action="install_plugin",
                resource_type="plugin_installation",
                resource_id=inst.id,
                result="success",
                metadata={"config": safe_config},
            )
        )

        result = dict(inst.__dict__)
        result.pop("_sa_instance_state", None)
        result["ok"] = True
        return result
    finally:
        if own_session:
            session.close()


def enable_plugin(
    organization_id: str,
    installation_id: str,
    actor_id: str = "system",
    db: Session | None = None,
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        repo = MarketplaceRepository(session)
        audit = AuditService(session)

        inst = repo.get_installation(organization_id, installation_id)
        if not inst:
            return {"ok": False, "error": "INSTALLATION_NOT_FOUND"}

        inst.enabled = True
        inst.status = PluginInstallStatus.enabled.value
        inst.updated_at = utc_now()
        repo.update_installation(inst)

        event_bus.emit(
            "marketplace.plugin.enabled",
            "plugin_service",
            f"Plugin {inst.plugin_id} enabled",
            {"installation_id": installation_id, "organization_id": organization_id},
        )
        audit.log(
            AuditLogCreate(
                actor_user_id=actor_id,
                actor_email="",
                action="enable_plugin",
                resource_type="plugin_installation",
                resource_id=installation_id,
                result="success",
            )
        )
        return {"ok": True}
    finally:
        if own_session:
            session.close()


def disable_plugin(
    organization_id: str,
    installation_id: str,
    actor_id: str = "system",
    db: Session | None = None,
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        repo = MarketplaceRepository(session)
        audit = AuditService(session)

        inst = repo.get_installation(organization_id, installation_id)
        if not inst:
            return {"ok": False, "error": "INSTALLATION_NOT_FOUND"}

        inst.enabled = False
        inst.status = PluginInstallStatus.disabled.value
        inst.updated_at = utc_now()
        repo.update_installation(inst)

        event_bus.emit(
            "marketplace.plugin.disabled",
            "plugin_service",
            f"Plugin {inst.plugin_id} disabled",
            {"installation_id": installation_id, "organization_id": organization_id},
        )
        audit.log(
            AuditLogCreate(
                actor_user_id=actor_id,
                actor_email="",
                action="disable_plugin",
                resource_type="plugin_installation",
                resource_id=installation_id,
                result="success",
            )
        )
        return {"ok": True}
    finally:
        if own_session:
            session.close()


def uninstall_plugin(
    organization_id: str,
    installation_id: str,
    actor_id: str = "system",
    db: Session | None = None,
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        repo = MarketplaceRepository(session)
        audit = AuditService(session)

        inst = repo.get_installation(organization_id, installation_id)
        if not inst:
            return {"ok": False, "error": "INSTALLATION_NOT_FOUND"}

        plugin_id = inst.plugin_id
        repo.delete_installation(inst)

        event_bus.emit(
            "marketplace.plugin.uninstalled",
            "plugin_service",
            f"Plugin {plugin_id} uninstalled",
            {"installation_id": installation_id, "organization_id": organization_id},
        )
        audit.log(
            AuditLogCreate(
                actor_user_id=actor_id,
                actor_email="",
                action="uninstall_plugin",
                resource_type="plugin_installation",
                resource_id=installation_id,
                result="success",
            )
        )
        return {"ok": True}
    finally:
        if own_session:
            session.close()


def list_plugins(
    search: str | None = None,
    category: str | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    with SessionLocal() as session:
        seed_builtins(session)
        plugins = registry_list_plugins(
            session,
            search=search,
            category=category,
            status=status,
        )
        return [manifest_to_dict(plugin) for plugin in plugins]


def run_plugin_action(
    organization_id: str,
    installation_id: str,
    action: str,
    payload: dict[str, Any],
    actor_id: str = "system",
    db: Session | None = None,
) -> dict[str, Any]:
    session, own_session = _session(db)
    try:
        repo = MarketplaceRepository(session)
        audit = AuditService(session)

        inst = repo.get_installation(organization_id, installation_id)
        if not inst:
            return {"ok": False, "error": "INSTALLATION_NOT_FOUND"}

        if not inst.enabled:
            return {"ok": False, "error": "PLUGIN_DISABLED"}

        plugin_id = inst.plugin_id
        safe_payload = _redact_secrets(payload)

        event_bus.emit(
            "marketplace.plugin.action.started",
            "plugin_service",
            f"Running {action} on {plugin_id}",
            {
                "installation_id": installation_id,
                "action": action,
                "payload": safe_payload,
            },
        )

        ok, msg = check_plugin_action(action, payload)
        if not ok:
            event_bus.emit(
                "marketplace.plugin.action.blocked",
                "plugin_service",
                f"Action {action} blocked: {msg}",
                {"installation_id": installation_id, "action": action, "reason": msg},
            )
            audit.log(
                AuditLogCreate(
                    actor_user_id=actor_id,
                    actor_email="",
                    action="run_plugin_action",
                    resource_type="plugin_installation",
                    resource_id=installation_id,
                    result="blocked",
                    metadata={"reason": msg},
                )
            )
            return {"ok": False, "error": msg}

        result_model = run_action(
            db=session,
            plugin_id=plugin_id,
            action=action,
            payload=payload,
            dry_run=True,
            installation_id=installation_id,
        )
        result = result_model.model_dump()

        event_bus.emit(
            "marketplace.plugin.action.completed",
            "plugin_service",
            f"Action {action} completed on {plugin_id}",
            {
                "installation_id": installation_id,
                "action": action,
                "result": _redact_secrets(result.get("output", {})),
            },
        )
        audit.log(
            AuditLogCreate(
                actor_user_id=actor_id,
                actor_email="",
                action="run_plugin_action",
                resource_type="plugin_installation",
                resource_id=installation_id,
                result="success",
                metadata={"action": action, "plugin_id": plugin_id},
            )
        )

        return result
    finally:
        if own_session:
            session.close()
