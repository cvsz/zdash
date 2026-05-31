from __future__ import annotations

from unittest.mock import patch

import pytest

from app.api import marketplace
from app.auth.models import AuthSession
from app.marketplace.builtins import BUILTINS
from app.tenancy.tenant_context import TenantContext


@pytest.fixture(autouse=True)
def marketplace_guards():
    with (
        patch("app.billing.entitlement_service.check_feature") as mock_billing_feat,
        patch("app.api.marketplace.consume") as mock_api_consume,
        patch("app.marketplace.plugin_service.check_feature") as mock_feat,
        patch("app.marketplace.plugin_service.consume") as mock_consume,
        patch("app.marketplace.plugin_service.AuditService.log"),
        patch("app.marketplace.plugin_service.event_bus"),
    ):

        class MockDecision:
            allowed = True

        mock_billing_feat.return_value = MockDecision()
        mock_api_consume.return_value = MockDecision()
        mock_feat.return_value = MockDecision()
        mock_consume.return_value = MockDecision()
        yield


def _admin() -> AuthSession:
    return AuthSession(username="test@zeaz.dev", role="admin")


def _viewer() -> AuthSession:
    return AuthSession(username="viewer@zeaz.dev", role="viewer")


_unique = 0


def _tenant() -> TenantContext:
    global _unique
    _unique += 1
    return TenantContext(
        organization_id=f"test-org-{_unique}",
        workspace_id=f"test-ws-{_unique}",
    )


def _install_req(plugin_id: str, ws: str) -> marketplace.InstallPluginRequest:
    return marketplace.InstallPluginRequest(
        plugin_id=plugin_id, workspace_id=ws, config={}
    )


def _assert_envelope(res: dict) -> None:
    assert "ok" in res
    assert "data" in res
    assert "error" in res
    assert "timestamp" in res


def test_categories_returns_envelope():
    res = marketplace.api_categories(current_user=_admin())
    _assert_envelope(res)
    assert res["ok"] is True
    assert "categories" in res["data"]


def test_list_plugins_returns_envelope():
    res = marketplace.api_plugins(current_user=_admin())
    _assert_envelope(res)
    assert res["ok"] is True
    assert "plugins" in res["data"]


def test_get_plugin_returns_envelope():
    res = marketplace.api_plugin(BUILTINS[0].id, current_user=_admin())
    _assert_envelope(res)
    assert res["ok"] is True
    assert "plugin" in res["data"]


def test_get_plugin_not_found_returns_error():
    res = marketplace.api_plugin("nonexistent-id", current_user=_admin())
    _assert_envelope(res)
    assert res["ok"] is False
    assert res["error"]["code"] == "PLUGIN_NOT_FOUND"


def test_install_returns_envelope():
    t = _tenant()
    res = marketplace.api_install(
        _install_req(BUILTINS[0].id, t.workspace_id or "ws"),
        current_user=_admin(),
        _f="feature.marketplace",
        tenant=t,
    )
    _assert_envelope(res)
    assert res["ok"] is True


def test_installations_returns_envelope():
    res = marketplace.api_installations(
        current_user=_admin(),
        tenant=_tenant(),
    )
    _assert_envelope(res)
    assert res["ok"] is True
    assert "installations" in res["data"]


def test_install_then_enable_then_disable_then_uninstall():
    t = _tenant()
    install_res = marketplace.api_install(
        _install_req(BUILTINS[0].id, t.workspace_id or "ws"),
        current_user=_admin(),
        _f="feature.marketplace",
        tenant=t,
    )
    _assert_envelope(install_res)
    assert install_res["ok"] is True
    inst_id = install_res["data"]["id"]

    enable_res = marketplace.api_enable(
        inst_id,
        current_user=_admin(),
        tenant=t,
    )
    _assert_envelope(enable_res)
    assert enable_res["ok"] is True

    run_res = marketplace.api_run(
        inst_id,
        marketplace.RunPluginRequest(action="test_action", payload={}),
        current_user=_admin(),
        tenant=t,
    )
    _assert_envelope(run_res)
    assert run_res["ok"] is True

    disable_res = marketplace.api_disable(
        inst_id,
        current_user=_admin(),
        tenant=t,
    )
    _assert_envelope(disable_res)
    assert disable_res["ok"] is True

    uninstall_res = marketplace.api_uninstall(
        inst_id,
        current_user=_admin(),
        tenant=t,
    )
    _assert_envelope(uninstall_res)
    assert uninstall_res["ok"] is True


def test_run_with_disabled_plugin_returns_envelope():
    t = _tenant()
    install_res = marketplace.api_install(
        _install_req(BUILTINS[0].id, t.workspace_id or "ws"),
        current_user=_admin(),
        _f="feature.marketplace",
        tenant=t,
    )
    inst_id = install_res["data"]["id"]

    marketplace.api_disable(
        inst_id,
        current_user=_admin(),
        tenant=t,
    )

    run_res = marketplace.api_run(
        inst_id,
        marketplace.RunPluginRequest(action="some_action", payload={}),
        current_user=_admin(),
        tenant=t,
    )
    _assert_envelope(run_res)
    assert run_res["ok"] is False
    assert run_res["error"]["code"] == "RUN_FAILED"


def test_uninstall_nonexistent_returns_envelope():
    res = marketplace.api_uninstall(
        "nonexistent-installation",
        current_user=_admin(),
        tenant=_tenant(),
    )
    _assert_envelope(res)
    assert res["ok"] is False


def test_register_manifest_envelope():
    res = marketplace.api_register_manifest(
        marketplace.RegisterManifestRequest(
            name="Test Register",
            slug="test-register",
            entrypoint="builtin://test",
            safety_level="sandbox",
            status="draft",
        ),
        current_user=_admin(),
    )
    _assert_envelope(res)
    assert res["ok"] is True
    assert "manifest" in res["data"]


def test_register_manifest_forbidden_for_viewer():
    res = marketplace.api_register_manifest(
        marketplace.RegisterManifestRequest(
            name="Test",
            slug="test",
            entrypoint="builtin://test",
            safety_level="sandbox",
        ),
        current_user=_viewer(),
    )
    _assert_envelope(res)
    assert res["ok"] is False
    assert res["error"]["code"] == "FORBIDDEN"
