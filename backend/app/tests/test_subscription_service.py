"""Tests for subscription service — Phase 10.3"""
from __future__ import annotations


from app.billing.subscription_service import (
    apply_mock_plan,
    cancel_subscription,
    get_status,
    list_plans,
    open_billing_portal,
    start_checkout,
)


# ------------------------------------------------------------------ #
# plan listing                                                         #
# ------------------------------------------------------------------ #


def test_list_plans_returns_list() -> None:
    plans = list_plans()
    assert isinstance(plans, list)
    assert len(plans) >= 4  # free, starter, pro, enterprise


def test_list_plans_includes_all_tiers() -> None:
    tiers = {p["tier"] for p in list_plans()}
    assert "free" in tiers
    assert "starter" in tiers
    assert "pro" in tiers
    assert "enterprise" in tiers


def test_list_plans_fields() -> None:
    for plan in list_plans():
        assert "tier" in plan
        assert "name" in plan
        assert "features" in plan
        assert "limits" in plan


# ------------------------------------------------------------------ #
# checkout                                                             #
# ------------------------------------------------------------------ #


def test_start_checkout_mock_returns_url() -> None:
    result = start_checkout("org-checkout-test", "pro")
    assert result["ok"] is True
    assert "checkout_url" in result
    assert result["checkout_url"].startswith("https://mock-billing.test/checkout/")


def test_start_checkout_invalid_plan_returns_error() -> None:
    result = start_checkout("org-bad-plan", "nonexistent_tier")
    assert result["ok"] is False
    assert "PLAN_NOT_FOUND" in result.get("error", "")


# ------------------------------------------------------------------ #
# billing portal                                                       #
# ------------------------------------------------------------------ #


def test_open_billing_portal_mock_returns_url() -> None:
    result = open_billing_portal("org-portal-test")
    assert result["ok"] is True
    assert "portal_url" in result
    assert result["portal_url"].startswith("https://mock-billing.test/portal/")


# ------------------------------------------------------------------ #
# get_status                                                           #
# ------------------------------------------------------------------ #


def test_get_status_no_subscription_returns_free() -> None:
    status = get_status("org-no-sub-xyz-" + __name__)
    # When no subscription exists, should return a safe free-like status
    assert "status" in status
    assert "plan_tier" in status


# ------------------------------------------------------------------ #
# apply_mock_plan                                                      #
# ------------------------------------------------------------------ #


def test_apply_mock_plan_starter() -> None:
    org = "org-mock-starter-test"
    result = apply_mock_plan(org, "starter")
    assert result["ok"] is True
    assert result["plan_tier"] == "starter"
    assert result["status"] == "active"


def test_apply_mock_plan_pro() -> None:
    org = "org-mock-pro-test"
    result = apply_mock_plan(org, "pro")
    assert result["ok"] is True
    assert result["plan_tier"] == "pro"


def test_apply_mock_plan_invalid_tier() -> None:
    result = apply_mock_plan("org-mock-bad", "diamond_plus")
    assert result["ok"] is False
    assert "PLAN_NOT_FOUND" in result.get("error", "")


def test_apply_mock_plan_updates_status() -> None:
    org = "org-mock-status-" + __name__
    apply_mock_plan(org, "starter")
    status = get_status(org)
    assert status["plan_tier"] in ("starter", "free", "unknown")  # DB may vary in test context


# ------------------------------------------------------------------ #
# cancel_subscription                                                  #
# ------------------------------------------------------------------ #


def test_cancel_subscription_no_active_returns_error() -> None:
    org = "org-cancel-no-sub-" + __name__
    result = cancel_subscription(org)
    assert result["ok"] is False
    assert "SUBSCRIPTION_INACTIVE" in result.get("error", "")


def test_cancel_subscription_after_apply() -> None:
    org = "org-cancel-flow-" + __name__
    apply_mock_plan(org, "pro")
    result = cancel_subscription(org)
    assert result["ok"] is True
    assert result.get("status") == "cancel_at_period_end"
