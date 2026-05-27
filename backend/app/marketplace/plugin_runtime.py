def run_action(plugin_id: str, action: str, payload: dict | None = None):
    return {
        "plugin_id": plugin_id,
        "action": action,
        "ok": True,
        "message": "dry-run",
        "output": payload or {},
        "dry_run": True,
    }
