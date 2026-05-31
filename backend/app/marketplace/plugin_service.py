from typing import Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy import select
from app.db.session import SessionLocal
from app.marketplace.models import PluginInstallation, PluginInstallStatus, PluginManifest, PluginStatus
from app.marketplace.plugin_runtime import run_action
from app.marketplace.plugin_registry import list_plugins as registry_list_plugins, seed_builtins
from app.marketplace.safety import check_plugin_action
from app.billing.entitlement_service import check_feature
from app.billing.quota_service import consume
from app.core.events import event_bus
from app.audit.audit_service import AuditService
from app.audit.models import AuditLogCreate
from app.db.repositories import MarketplaceRepository


SECRET_KEYS = {"secret", "password", "token", "key", "credential"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _redact_secrets(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return payload
    redacted: dict[str, Any] = {}
    for k, v in payload.items():
        if any(s in k.lower() for s in SECRET_KEYS):
            redacted[k] = "***REDACTED***"
        elif isinstance(v, dict):
            redacted[k] = _redact_secrets(v)
        else:
            redacted[k] = v
    return redacted


def validate_install(
    organization_id: str,
    plugin_id: str,
    workspace_id: str,
    config: dict[str, Any] | None = None,
    db: Any | None = None,
) -> Dict[str, Any]:
    own_session = db is None
    if own_session:
        db = SessionLocal()
        seed_builtins(db)
    try:
        manifest = db.execute(
            select(PluginManifest).where(PluginManifest.id == plugin_id)
        ).scalar_one_or_none()

        if not manifest:
            return {"ok": False, "error": "PLUGIN_NOT_FOUND"}

        if manifest.status not in (PluginStatus.approved.value,):
            return {"ok": False, "error": "PLUGIN_NOT_APPROVED"}

        repo = MarketplaceRepository(db)
        existing = repo.list_installations(organization_id, workspace_id)
        for inst in existing:
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

        return {"ok": True, "manifest": manifest}
    finally:
        if own_session:
            db.close()


def list_installations(
    organization_id: str, workspace_id: str | None = None
) -> List[PluginInstallation]:
    with SessionLocal() as db:
        repo = MarketplaceRepository(db)
        return repo.list_installations(organization_id, workspace_id)


def install_plugin(
    organization_id: str,
    plugin_id: str,
    workspace_id: str,
    config: dict[str, Any] | None = None,
    installed_by: str = "system",
    db: Any | None = None,
) -> Dict[str, Any]:
    validation = validate_install(
        organization_id, plugin_id, workspace_id, config, db=db
    )
    if not validation.get("ok"):
        return validation

    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        repo = MarketplaceRepository(db)
        audit = AuditService(db)

        inst = repo.create_installation(
            organization_id=organization_id,
            workspace_id=workspace_id,
            plugin_id=plugin_id,
            version="1.0.0",
            status=PluginInstallStatus.installed,
            config_json=config or {},
            enabled=False,
            installed_by=installed_by,
        )

        safe_config = _redact_secrets(config or {})
        event_bus.emit(
            "marketplace.plugin.installed",
            "plugin_service",
            f"Plugin {plugin_id} installed",
            _redact_secrets({
                "plugin_id": plugin_id,
                "installation_id": inst.id,
                "organization_id": organization_id,
                "workspace_id": workspace_id,
                "config": safe_config,
            }),
        )

        audit.log(
            AuditLogCreate(
                actor_user_id=installed_by,
                actor_email="",
                action="install_plugin",
                resource_type="plugin_installation",
                resource_id=inst.id,
                result="success",
                metadata=_redact_secrets({"config": safe_config}),
            )
        )

        ret = dict(inst.__dict__)
        ret.pop("_sa_instance_state", None)
        ret["ok"] = True
        return ret
    finally:
        if own_session:
            db.close()


def enable_plugin(
    organization_id: str,
    installation_id: str,
    actor_id: str = "system",
    db: Any | None = None,
) -> Dict[str, Any]:
    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        repo = MarketplaceRepository(db)
        audit = AuditService(db)
        inst = repo.get_installation(organization_id, installation_id)
        if not inst:
            return {"ok": False, "error": "INSTALLATION_NOT_FOUND"}

        inst.enabled = True
        inst.status = PluginInstallStatus.enabled
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
            db.close()


def disable_plugin(
    organization_id: str,
    installation_id: str,
    actor_id: str = "system",
    db: Any | None = None,
) -> Dict[str, Any]:
    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        repo = MarketplaceRepository(db)
        audit = AuditService(db)
        inst = repo.get_installation(organization_id, installation_id)
        if not inst:
            return {"ok": False, "error": "INSTALLATION_NOT_FOUND"}

        inst.enabled = False
        inst.status = PluginInstallStatus.disabled
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
            db.close()


def uninstall_plugin(
    organization_id: str,
    installation_id: str,
    actor_id: str = "system",
    db: Any | None = None,
) -> Dict[str, Any]:
    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        repo = MarketplaceRepository(db)
        audit = AuditService(db)
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
            db.close()


def list_plugins(
    search: str | None = None,
    category: str | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    with SessionLocal() as db:
        seed_builtins(db)
        return registry_list_plugins(db, search=search, category=category, status=status)


def run_plugin_action(
    organization_id: str,
    installation_id: str,
    action: str,
    payload: dict,
    actor_id: str = "system",
    db: Any | None = None,
) -> Dict[str, Any]:
    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        repo = MarketplaceRepository(db)
        audit = AuditService(db)
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
            _redact_secrets({
                "installation_id": installation_id,
                "action": action,
                "payload": safe_payload,
            }),
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

        result = run_action(
            db=db,
            plugin_id=plugin_id,
            action=action,
            payload=payload,
            dry_run=True,
        )
        if hasattr(result, "model_dump"):
            result = result.model_dump()

        event_bus.emit(
            "marketplace.plugin.action.completed",
            "plugin_service",
            f"Action {action} completed on {plugin_id}",
            _redact_secrets({
                "installation_id": installation_id,
                "action": action,
                "result": result.get("output", {}),
            }),
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
            db.close()
