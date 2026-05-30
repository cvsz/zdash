from __future__ import annotations

from unittest.mock import patch

import pytest

from app.api import enterprise
from app.auth.models import AuthSession


@pytest.fixture(autouse=True)
def enterprise_guards():
    with (
        patch("app.api.enterprise.require_permissions") as mock_perm,
        patch("app.api.enterprise.require_feature") as mock_feat,
        patch("app.api.enterprise.get_branding") as mock_brand,
        patch("app.api.enterprise.update_branding") as mock_update_brand,
        patch("app.api.enterprise.reset_branding") as mock_reset_brand,
        patch("app.api.enterprise.get_license_status") as mock_license,
        patch("app.api.enterprise.apply_license") as mock_apply,
        patch("app.api.enterprise.revoke_license") as mock_revoke,
        patch("app.api.enterprise.list_export_bundles") as mock_list_exports,
        patch("app.api.enterprise.create_export_bundle") as mock_create_export,
        patch("app.api.enterprise.get_export_bundle") as mock_get_export,
        patch("app.api.enterprise.get_checklist") as mock_checklist,
        patch("app.api.enterprise.mark_step_complete") as mock_step,
        patch("app.api.enterprise.reset_checklist") as mock_reset,
        patch("app.api.enterprise.get_customer_health") as mock_health,
    ):
        mock_perm.return_value = lambda x: None

        class MockDecision:
            allowed = True

        mock_feat.return_value = MockDecision()
        mock_brand.return_value = {"name": "zDash", "primary_color": "#7c3aed"}
        mock_update_brand.return_value = {"name": "zDash", "updated": True}
        mock_reset_brand.return_value = {"name": "zDash", "reset": True}
        mock_license.return_value = {"status": "active", "tier": "enterprise"}
        mock_apply.return_value = {"status": "active", "license_key": "test-license"}
        mock_revoke.return_value = {"status": "revoked"}
        mock_list_exports.return_value = []
        mock_create_export.return_value = {
            "bundle_id": "export-1",
            "export_type": "full",
            "status": "pending",
        }
        mock_get_export.return_value = {
            "bundle_id": "export-1",
            "export_type": "full",
            "status": "completed",
        }
        mock_checklist.return_value = {"steps": [], "completed": 0}
        mock_step.return_value = {"steps": [{"name": "setup", "done": True}], "completed": 1}
        mock_reset.return_value = {"steps": [], "completed": 0}
        mock_health.return_value = {"status": "healthy", "score": 85}
        yield


def _admin() -> AuthSession:
    return AuthSession(username="enterprise-admin", role="admin")


def _viewer() -> AuthSession:
    return AuthSession(username="viewer", role="viewer")


def test_status_returns_license_and_branding() -> None:
    result = enterprise.api_status(current_user=_admin())
    assert result["ok"] is True
    assert "license" in result["data"]
    assert result["data"]["license"]["status"] == "active"


def test_license_status_endpoint() -> None:
    result = enterprise.api_license_status(current_user=_admin())
    assert result["ok"] is True
    assert result["data"]["status"] == "active"


def test_license_apply() -> None:
    req = enterprise.ApplyLicenseRequest(license_key="test-license")
    result = enterprise.api_license_apply(req, current_user=_admin())
    assert result["ok"] is True
    assert result["data"]["license_key"] == "test-license"


def test_license_revoke() -> None:
    result = enterprise.api_license_revoke(current_user=_admin())
    assert result["ok"] is True
    assert result["data"]["status"] == "revoked"


def test_branding_get() -> None:
    result = enterprise.api_branding(current_user=_admin())
    assert result["ok"] is True
    assert result["data"]["name"] == "zDash"


def test_branding_update() -> None:
    result = enterprise.api_branding_patch(
        {"name": "zDash Pro", "primary_color": "#22D3EE"},
        current_user=_admin(),
    )
    assert result["ok"] is True
    assert result["data"]["updated"] is True


def test_branding_reset() -> None:
    result = enterprise.api_branding_reset(current_user=_admin())
    assert result["ok"] is True
    assert result["data"]["reset"] is True


def test_exports_list() -> None:
    result = enterprise.api_exports(current_user=_admin())
    assert result["ok"] is True
    assert isinstance(result["data"]["exports"], list)


def test_export_create() -> None:
    req = enterprise.ExportRequest(export_type="full")
    result = enterprise.api_create_export(req, current_user=_admin())
    assert result["ok"] is True
    assert result["data"]["status"] == "pending"


def test_export_create_with_secrets_requires_confirmation() -> None:
    req = enterprise.ExportRequest(include_secrets=True, secret_export_confirmation="")
    result = enterprise.api_create_export(req, current_user=_admin())
    assert result["ok"] is False
    assert "CONFIRM" in result["error"]["code"]


def test_export_get() -> None:
    result = enterprise.api_export_get("export-1", current_user=_admin())
    assert result["ok"] is True
    assert result["data"]["bundle_id"] == "export-1"


def test_onboarding_checklist() -> None:
    result = enterprise.api_onboarding(current_user=_admin())
    assert result["ok"] is True
    assert "steps" in result["data"]


def test_onboarding_step() -> None:
    req = enterprise.OnboardingStepRequest(step="setup")
    result = enterprise.api_onboarding_step(req, current_user=_admin())
    assert result["ok"] is True
    assert result["data"]["completed"] == 1


def test_onboarding_reset() -> None:
    result = enterprise.api_onboarding_reset(current_user=_admin())
    assert result["ok"] is True
    assert result["data"]["completed"] == 0


def test_customer_health() -> None:
    result = enterprise.api_health(current_user=_admin())
    assert result["ok"] is True
    assert result["data"]["status"] == "healthy"


def test_secret_export_requires_permission() -> None:
    req = enterprise.ExportRequest(
        include_secrets=True,
        secret_export_confirmation="CONFIRM_SECRET_EXPORT",
    )
    with patch("app.api.enterprise.has_permission", return_value=False):
        result = enterprise.api_create_export(req, current_user=_viewer())
    assert result["ok"] is False
    assert "SECRET_EXPORT_DENIED" in result["error"]["code"]
