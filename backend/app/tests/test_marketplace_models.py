from datetime import UTC, datetime

from app.marketplace.models import (
    PluginActionResult,
    PluginInstallation,
    PluginInstallStatus,
    PluginManifest,
    PluginStatus,
    installation_to_dict,
    manifest_to_dict,
)


def test_plugin_manifest_model():
    manifest = PluginManifest(
        id="test-plugin",
        name="Test Plugin",
        slug="test-plugin",
        version="1.0.0",
        description="A test plugin",
        author="test",
        category="general",
        status=PluginStatus.approved.value,
    )
    assert manifest.id == "test-plugin"
    assert manifest.name == "Test Plugin"

    d = manifest_to_dict(manifest)
    assert d["id"] == "test-plugin"
    assert d["name"] == "Test Plugin"
    assert d["status"] == "approved"


def test_plugin_installation_model():
    inst = PluginInstallation(
        id="inst-1",
        organization_id="org-1",
        workspace_id="ws-1",
        plugin_id="plugin-1",
        version="1.0.0",
        status=PluginInstallStatus.installed.value,
        config_json={"key": "value"},
        enabled=True,
        installed_by="user-1",
        installed_at=datetime.now(UTC),
    )
    assert inst.id == "inst-1"
    assert inst.organization_id == "org-1"

    d = installation_to_dict(inst)
    assert d["id"] == "inst-1"
    assert d["organization_id"] == "org-1"
    assert d["status"] == "installed"
    assert d["enabled"] is True
    assert d["config"] == {"key": "value"}


def test_plugin_action_result_schema():
    res = PluginActionResult(
        plugin_id="plugin-1",
        action="test_action",
        ok=True,
        message="Success",
        output={"data": "test"},
        dry_run=True,
        timestamp=datetime.now(UTC),
    )
    assert res.plugin_id == "plugin-1"
    assert res.action == "test_action"
    assert res.ok is True
    assert res.output == {"data": "test"}
