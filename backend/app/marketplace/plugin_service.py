from .plugin_store import INSTALLS
from .plugin_runtime import run_action
from .safety import check_plugin_action


def list_installations(org_id: str):
    return [i for i in INSTALLS if i["organization_id"] == org_id]


def install_plugin(organization_id, plugin_id, workspace_id, config=None):
    item = {
        "id": f"inst-{len(INSTALLS) + 1}",
        "organization_id": organization_id,
        "workspace_id": workspace_id,
        "plugin_id": plugin_id,
        "enabled": False,
        "config": config or {},
    }
    INSTALLS.append(item)
    return item


def enable_plugin(installation_id):
    for i in INSTALLS:
        if i["id"] == installation_id:
            i["enabled"] = True
            return i
    return None


def disable_plugin(installation_id):
    for i in INSTALLS:
        if i["id"] == installation_id:
            i["enabled"] = False
            return i
    return None


def uninstall_plugin(installation_id):
    global INSTALLS
    INSTALLS = [i for i in INSTALLS if i["id"] != installation_id]
    return {"ok": True}


def run_plugin_action(installation_id, action, payload):
    inst = next(i for i in INSTALLS if i["id"] == installation_id)
    ok, msg = check_plugin_action(action, payload)
    if not ok:
        return {"ok": False, "error": msg}
    return run_action(inst["plugin_id"], action, payload)
