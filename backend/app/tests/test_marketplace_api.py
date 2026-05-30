from __future__ import annotations

from unittest.mock import patch

import pytest

from app.api import marketplace
from app.auth.models import AuthSession
from app.marketplace.plugin_registry import BUILTINS
from app.tenancy.tenant_context import TenantContext


@pytest.fixture(autouse=True)
def marketplace_guards():
    with (
        patch("app.billing.entitlement_service.check_feature") as mock_billing_feat,
        patch("app.api.marketplace.consume") as mock_api_consume,
        patch("app.marketplace.plugin_service.check_feature") as mock_feat,
        patch("app.marketplace.plugin_service.consume") as mock_consume,
        patch("app.marketplace.plugin_service.AuditService.log"),
    ):

        class MockDecision:
            allowed = True

        mock_billing_feat.return_value = MockDecision()
        mock_api_consume.return_value = MockDecision()
        mock_feat.return_value = MockDecision()
        mock_consume.return_value = MockDecision()
        yield


def _admin() -> AuthSession:
    return AuthSession(username="test_marketplace@zeaz.dev", role="admin")


def _tenant() -> TenantContext:
    return TenantContext(organization_id="test-marketplace-org", workspace_id="test-ws")


def test_list_plugins_api() -> None:
    res = marketplace.api_plugins(current_user=_admin())

    assert res["ok"] is True
    assert len(res["data"]["plugins"]) == len(BUILTINS)


def test_get_plugin_api() -> None:
    res = marketplace.api_plugin(BUILTINS[0].id, current_user=_admin())
    plugin = res["data"]["plugin"]

    assert res["ok"] is True
    assert getattr(plugin, "id", None) == BUILTINS[0].id


def test_install_and_lifecycle_api() -> None:
    install_res = marketplace.api_install(
        marketplace.InstallPluginRequest(
            plugin_id=BUILTINS[0].id,
            workspace_id="test-ws",
            config={},
        ),
        current_user=_admin(),
        _f="feature.marketplace",
        tenant=_tenant(),
    )
    assert install_res["ok"] is True
    inst_id = install_res["data"]["id"]

    enable_res = marketplace.api_enable(
        inst_id,
        current_user=_admin(),
        tenant=_tenant(),
    )
    assert enable_res["ok"] is True

    run_res = marketplace.api_run(
        inst_id,
        marketplace.RunPluginRequest(action="test_action", payload={}),
        current_user=_admin(),
        tenant=_tenant(),
    )
    assert run_res["ok"] is True

    disable_res = marketplace.api_disable(
        inst_id,
        current_user=_admin(),
        tenant=_tenant(),
    )
    assert disable_res["ok"] is True

    uninstall_res = marketplace.api_uninstall(
        inst_id,
        current_user=_admin(),
        tenant=_tenant(),
    )
    assert uninstall_res["ok"] is True
