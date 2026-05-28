"""Tests for mock billing adapter — Phase 10.3"""
from __future__ import annotations

import pytest

from app.billing.mock_billing_adapter import MockBillingAdapter


@pytest.fixture()
def adapter() -> MockBillingAdapter:
    return MockBillingAdapter()


class _Org:
    def __init__(self, org_id: str, name: str = "Test Org") -> None:
        self.id = org_id
        self.name = name


# ------------------------------------------------------------------ #
# customer IDs                                                         #
# ------------------------------------------------------------------ #


def test_create_customer_returns_string(adapter: MockBillingAdapter) -> None:
    cus_id = adapter.create_customer(_Org("org-abc"))
    assert isinstance(cus_id, str)
    assert cus_id.startswith("cus_mock_")


def test_create_customer_is_deterministic(adapter: MockBillingAdapter) -> None:
    org = _Org("org-stable")
    assert adapter.create_customer(org) == adapter.create_customer(org)


def test_create_customer_differs_per_org(adapter: MockBillingAdapter) -> None:
    assert adapter.create_customer(_Org("org-1")) != adapter.create_customer(_Org("org-2"))


# ------------------------------------------------------------------ #
# checkout URLs                                                        #
# ------------------------------------------------------------------ #


def test_checkout_url_starts_with_base(adapter: MockBillingAdapter) -> None:
    url = adapter.create_checkout_session("org-x", "pro")
    assert url.startswith("https://mock-billing.test/checkout/")


def test_checkout_url_is_deterministic(adapter: MockBillingAdapter) -> None:
    url1 = adapter.create_checkout_session("org-y", "starter")
    url2 = adapter.create_checkout_session("org-y", "starter")
    assert url1 == url2


def test_checkout_url_differs_per_plan(adapter: MockBillingAdapter) -> None:
    url_pro = adapter.create_checkout_session("org-z", "pro")
    url_starter = adapter.create_checkout_session("org-z", "starter")
    assert url_pro != url_starter


# ------------------------------------------------------------------ #
# billing portal URLs                                                  #
# ------------------------------------------------------------------ #


def test_portal_url_starts_with_base(adapter: MockBillingAdapter) -> None:
    portal = adapter.create_billing_portal_session("org-portal")
    assert portal.startswith("https://mock-billing.test/portal/")


def test_portal_url_is_deterministic(adapter: MockBillingAdapter) -> None:
    p1 = adapter.create_billing_portal_session("org-p")
    p2 = adapter.create_billing_portal_session("org-p")
    assert p1 == p2


# ------------------------------------------------------------------ #
# get_subscription                                                     #
# ------------------------------------------------------------------ #


def test_get_subscription_returns_none(adapter: MockBillingAdapter) -> None:
    # Mock adapter has no live state — always returns None
    result = adapter.get_subscription("sub_anything")
    assert result is None


# ------------------------------------------------------------------ #
# cancel_subscription                                                  #
# ------------------------------------------------------------------ #


def test_cancel_subscription_returns_true(adapter: MockBillingAdapter) -> None:
    assert adapter.cancel_subscription("sub_fake") is True


# ------------------------------------------------------------------ #
# webhook                                                              #
# ------------------------------------------------------------------ #


def test_webhook_returns_ok(adapter: MockBillingAdapter) -> None:
    result = adapter.handle_webhook(b"payload", "sig123")
    assert result["ok"] is True
    assert "event" in result


def test_webhook_no_external_calls(adapter: MockBillingAdapter, monkeypatch) -> None:
    """Verify mock adapter never makes network calls."""
    import socket

    original_connect = socket.socket.connect

    def fail_connect(*args, **kwargs):  # type: ignore
        raise AssertionError("Mock adapter must not make network calls")

    monkeypatch.setattr(socket.socket, "connect", fail_connect)
    result = adapter.handle_webhook(b"test", "test-sig")
    assert result["ok"] is True
    monkeypatch.setattr(socket.socket, "connect", original_connect)
