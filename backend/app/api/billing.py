"""Billing API — Phase 10.3

Endpoints:
  GET  /api/billing/status
  GET  /api/billing/plans
  GET  /api/billing/subscription
  POST /api/billing/checkout
  POST /api/billing/portal
  POST /api/billing/cancel
  POST /api/billing/mock/apply-plan
  GET  /api/billing/usage
  GET  /api/billing/usage/{metric}
  GET  /api/billing/invoices
  POST /api/billing/webhooks/provider

Rules enforced:
- All endpoints except /webhooks/provider require authentication.
- Tenant-scoped via X-Organization-ID header (or auth token org_id).
- Admin / billing_manage can mutate; billing_read and usage_read can read.
- Webhook endpoint verifies provider signature when Stripe is enabled.
- All billing mutations emit audit events.
- Standard API response envelope used throughout.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.auth.dependencies import require_permissions
from app.auth.models import AuthSession
from app.auth.rbac import Permission
from app.billing.billing_webhooks import handle_webhook
from app.billing.invoice_service import get_invoices
from app.billing.subscription_service import (
    apply_mock_plan,
    cancel_subscription,
    get_status,
    list_plans,
    open_billing_portal,
    start_checkout,
)
from app.billing.usage_meter import get_metric_summary, get_usage_summary
from app.core.events import event_bus
from app.core.responses import error_response, success_response

router = APIRouter(prefix="/api/billing", tags=["billing"])


# ------------------------------------------------------------------ #
# Request bodies                                                       #
# ------------------------------------------------------------------ #


class CheckoutRequest(BaseModel):
    plan_id: str


class ApplyMockPlanRequest(BaseModel):
    plan_tier: str


# ------------------------------------------------------------------ #
# helpers                                                              #
# ------------------------------------------------------------------ #


def _org_id(user: AuthSession) -> str:
    org: str | None = getattr(user, "organization_id", None)
    return org or str(getattr(user, "username", "default"))


def _ws_id(user: AuthSession) -> str | None:
    return getattr(user, "workspace_id", None)


def _audit(action: str, user: AuthSession, extra: dict[str, Any] | None = None) -> None:
    event_bus.emit(
        "billing.subscription.updated",
        "api.billing",
        action,
        {"actor": user.username, "organization_id": _org_id(user), **(extra or {})},
    )


# ------------------------------------------------------------------ #
# Endpoints                                                            #
# ------------------------------------------------------------------ #


@router.get("/status")
def api_get_status(
    current_user: AuthSession = Depends(
        require_permissions([Permission.billing_read])
    ),
) -> dict:
    try:
        result = get_status(_org_id(current_user))
        return success_response(result)
    except Exception as exc:  # noqa: BLE001
        return error_response("BILLING_ERROR", str(exc))


@router.get("/plans")
def api_list_plans() -> dict:
    """Public — no auth required to list plans."""
    try:
        return success_response({"plans": list_plans()})
    except Exception as exc:  # noqa: BLE001
        return error_response("BILLING_ERROR", str(exc))


@router.get("/subscription")
def api_get_subscription(
    current_user: AuthSession = Depends(
        require_permissions([Permission.billing_read])
    ),
) -> dict:
    try:
        result = get_status(_org_id(current_user))
        return success_response(result)
    except Exception as exc:  # noqa: BLE001
        return error_response("BILLING_ERROR", str(exc))


@router.post("/checkout")
def api_checkout(
    req: CheckoutRequest,
    current_user: AuthSession = Depends(
        require_permissions([Permission.billing_manage])
    ),
) -> dict:
    org = _org_id(current_user)
    result = start_checkout(org, req.plan_id)
    if not result.get("ok"):
        code = result.get("error", "BILLING_ERROR")
        return error_response(
            code if code in ("BILLING_PROVIDER_NOT_CONFIGURED", "PLAN_NOT_FOUND") else "BILLING_ERROR",
            result.get("error", "Checkout failed"),
        )
    _audit("billing.checkout.started", current_user, {"plan_id": req.plan_id})
    return success_response({"checkout_url": result["checkout_url"]})


@router.post("/portal")
def api_portal(
    current_user: AuthSession = Depends(
        require_permissions([Permission.billing_manage])
    ),
) -> dict:
    org = _org_id(current_user)
    result = open_billing_portal(org)
    if not result.get("ok"):
        return error_response(
            "BILLING_PROVIDER_NOT_CONFIGURED", result.get("error", "Portal failed")
        )
    return success_response({"portal_url": result["portal_url"]})


@router.post("/cancel")
def api_cancel(
    current_user: AuthSession = Depends(
        require_permissions([Permission.billing_manage])
    ),
) -> dict:
    org = _org_id(current_user)
    result = cancel_subscription(org)
    if not result.get("ok"):
        code = result.get("error", "BILLING_ERROR")
        return error_response(
            code if code == "SUBSCRIPTION_INACTIVE" else "BILLING_ERROR",
            result.get("error", "Cancel failed"),
        )
    _audit("billing.subscription.canceled", current_user)
    return success_response(result)


@router.post("/mock/apply-plan")
def api_apply_mock_plan(
    req: ApplyMockPlanRequest,
    current_user: AuthSession = Depends(
        require_permissions([Permission.billing_apply_mock_plan])
    ),
) -> dict:
    org = _org_id(current_user)
    result = apply_mock_plan(org, req.plan_tier)
    if not result.get("ok"):
        code = result.get("error", "BILLING_ERROR")
        return error_response(
            code if code in ("PLAN_NOT_FOUND",) else "BILLING_ERROR",
            result.get("error", "Apply failed"),
        )
    _audit("billing.mock_plan.applied", current_user, {"plan_tier": req.plan_tier})
    return success_response(result)


@router.get("/usage")
def api_get_usage(
    current_user: AuthSession = Depends(
        require_permissions([Permission.usage_read])
    ),
) -> dict:
    try:
        org = _org_id(current_user)
        ws = _ws_id(current_user)
        result = get_usage_summary(org, ws)
        return success_response({"summary": result})
    except Exception as exc:  # noqa: BLE001
        return error_response("BILLING_ERROR", str(exc))


@router.get("/usage/{metric}")
def api_get_metric_usage(
    metric: str,
    current_user: AuthSession = Depends(
        require_permissions([Permission.usage_read])
    ),
) -> dict:
    try:
        org = _org_id(current_user)
        ws = _ws_id(current_user) or "default"
        result = get_metric_summary(org, ws, metric)
        return success_response(result)
    except Exception as exc:  # noqa: BLE001
        return error_response("BILLING_ERROR", str(exc))


@router.get("/invoices")
def api_get_invoices(
    current_user: AuthSession = Depends(
        require_permissions([Permission.billing_read])
    ),
) -> dict:
    try:
        org = _org_id(current_user)
        invoices = get_invoices(org)
        return success_response({"invoices": invoices})
    except Exception as exc:  # noqa: BLE001
        return error_response("BILLING_ERROR", str(exc))


@router.post("/webhooks/provider")
async def api_webhook(request: Request) -> dict:
    """Inbound provider webhook — no user auth, verifies provider signature."""
    try:
        payload = await request.body()
        signature = request.headers.get("stripe-signature", "")
        result = handle_webhook(payload, signature)
        if not result.get("ok"):
            raise HTTPException(status_code=400, detail=result.get("error", "Webhook failed"))
        return success_response(result)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
