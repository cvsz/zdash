"""Tests for Billing API endpoint functions."""

from __future__ import annotations

import asyncio

from app.api import billing
from app.auth.models import AuthSession


class _MockRequest:
    def __init__(self, body: bytes, headers: dict[str, str] | None = None) -> None:
        self._body = body
        self.headers = headers or {}

    async def body(self) -> bytes:
        return self._body


def _user(username: str = "billing-admin") -> AuthSession:
    return AuthSession(username=username, role="admin")


def test_plans_endpoint_returns_list() -> None:
    body = billing.api_list_plans()

    assert body["ok"] is True
    assert "plans" in body["data"]
    assert isinstance(body["data"]["plans"], list)
    assert len(body["data"]["plans"]) >= 4


def test_plans_endpoint_no_auth_required() -> None:
    assert billing.api_list_plans()["ok"] is True


def test_status_endpoint_authenticated() -> None:
    body = billing.api_get_status(current_user=_user())

    assert body["ok"] is True
    assert "status" in body["data"]


def test_subscription_endpoint() -> None:
    body = billing.api_get_subscription(current_user=_user())

    assert body["ok"] is True


def test_checkout_endpoint_valid_plan() -> None:
    body = billing.api_checkout(
        billing.CheckoutRequest(plan_id="pro"),
        current_user=_user(),
    )

    assert body["ok"] is True
    assert "checkout_url" in body["data"]
    assert "mock-billing.test" in body["data"]["checkout_url"]


def test_checkout_endpoint_invalid_plan() -> None:
    body = billing.api_checkout(
        billing.CheckoutRequest(plan_id="nonexistent"),
        current_user=_user(),
    )

    assert body["ok"] is False
    assert body["error"]["code"] in ("PLAN_NOT_FOUND", "BILLING_ERROR")


def test_portal_endpoint_returns_url() -> None:
    body = billing.api_portal(current_user=_user())

    assert body["ok"] is True
    assert "portal_url" in body["data"]


def test_cancel_no_subscription_returns_envelope() -> None:
    body = billing.api_cancel(current_user=_user("test-cancel-virgin-org-abc"))

    assert "ok" in body


def test_apply_mock_plan_endpoint() -> None:
    body = billing.api_apply_mock_plan(
        billing.ApplyMockPlanRequest(plan_tier="starter"),
        current_user=_user(),
    )

    assert body["ok"] is True
    assert body["data"]["plan_tier"] == "starter"


def test_apply_mock_plan_invalid_tier() -> None:
    body = billing.api_apply_mock_plan(
        billing.ApplyMockPlanRequest(plan_tier="diamond"),
        current_user=_user(),
    )

    assert body["ok"] is False


def test_usage_endpoint_returns_data() -> None:
    body = billing.api_get_usage(current_user=_user())

    assert body["ok"] is True


def test_metric_usage_endpoint() -> None:
    body = billing.api_get_metric_usage(
        "backtests_per_month",
        current_user=_user(),
    )

    assert body["ok"] is True


def test_invoices_endpoint_returns_list() -> None:
    body = billing.api_get_invoices(current_user=_user())

    assert body["ok"] is True
    assert "invoices" in body["data"]
    assert isinstance(body["data"]["invoices"], list)


def test_webhook_endpoint_mock_returns_ok() -> None:
    body = asyncio.run(
        billing.api_webhook(
            _MockRequest(
                body=b'{"type": "payment_intent.succeeded"}',
                headers={"Content-Type": "application/json"},
            )
        )
    )

    assert body["ok"] is True


def test_webhook_endpoint_no_auth_required() -> None:
    body = asyncio.run(billing.api_webhook(_MockRequest(body=b'{"type": "test"}')))

    assert body["ok"] is True
