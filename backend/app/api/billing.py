from fastapi import APIRouter, Depends, Request, HTTPException
from typing import Any, Dict
from pydantic import BaseModel

from app.auth.dependencies import get_current_user, require_permissions
from app.auth.rbac import Permission
from app.billing.subscription_service import get_status, list_plans, start_checkout, open_billing_portal, cancel_subscription, apply_mock_plan
from app.billing.usage_meter import get_usage_summary, get_metric_summary
from app.billing.invoice_service import get_invoices
from app.billing.billing_webhooks import handle_webhook
from app.core.responses import success_response, error_response

router = APIRouter()

class ApplyMockPlanRequest(BaseModel):
    plan_tier: str

class CheckoutRequest(BaseModel):
    plan_id: str

@router.get("/status")
def api_get_status(current_user: Any = Depends(get_current_user)):
    try:
        status = get_status(current_user.organization_id)
        return success_response(status)
    except Exception as e:
        return error_response("BILLING_ERROR", str(e))

@router.get("/plans")
def api_list_plans():
    return success_response(list_plans())

@router.post("/checkout")
def api_checkout(req: CheckoutRequest, current_user: Any = Depends(require_permissions([Permission.billing_manage]))):
    try:
        result = start_checkout(current_user.organization_id, req.plan_id)
        if not result.get("ok"):
            return error_response("CHECKOUT_FAILED", result.get("error", "Unknown error"))
        return success_response({"checkout_url": result["checkout_url"]})
    except Exception as e:
        return error_response("CHECKOUT_ERROR", str(e))

@router.post("/portal")
def api_portal(current_user: Any = Depends(require_permissions([Permission.billing_manage]))):
    try:
        result = open_billing_portal(current_user.organization_id)
        if not result.get("ok"):
            return error_response("PORTAL_FAILED", result.get("error", "Unknown error"))
        return success_response({"portal_url": result["portal_url"]})
    except Exception as e:
        return error_response("PORTAL_ERROR", str(e))

@router.post("/cancel")
def api_cancel(current_user: Any = Depends(require_permissions([Permission.billing_manage]))):
    try:
        result = cancel_subscription(current_user.organization_id)
        if not result.get("ok"):
            return error_response("CANCEL_FAILED", result.get("error", "Unknown error"))
        return success_response(result)
    except Exception as e:
        return error_response("CANCEL_ERROR", str(e))

@router.post("/mock/apply-plan")
def api_apply_mock_plan(req: ApplyMockPlanRequest, current_user: Any = Depends(require_permissions([Permission.billing_apply_mock_plan]))):
    try:
        result = apply_mock_plan(current_user.organization_id, req.plan_tier)
        if not result.get("ok"):
            return error_response("APPLY_FAILED", result.get("error", "Unknown error"))
        return success_response(result)
    except Exception as e:
        return error_response("APPLY_ERROR", str(e))

@router.get("/usage")
def api_get_usage(current_user: Any = Depends(require_permissions([Permission.usage_read]))):
    try:
        # If user is restricted to a workspace, only show that workspace's usage
        ws_id = current_user.workspace_id if hasattr(current_user, "workspace_id") else None
        usage = get_usage_summary(current_user.organization_id, ws_id)
        return success_response(usage)
    except Exception as e:
        return error_response("USAGE_ERROR", str(e))

@router.get("/usage/{metric}")
def api_get_metric_usage(metric: str, current_user: Any = Depends(require_permissions([Permission.usage_read]))):
    try:
        ws_id = current_user.workspace_id if hasattr(current_user, "workspace_id") else None
        usage = get_metric_summary(current_user.organization_id, ws_id, metric)
        return success_response(usage)
    except Exception as e:
        return error_response("USAGE_ERROR", str(e))

@router.get("/invoices")
def api_get_invoices(current_user: Any = Depends(require_permissions([Permission.billing_read]))):
    try:
        invoices = get_invoices(current_user.organization_id)
        return success_response(invoices)
    except Exception as e:
        return error_response("INVOICES_ERROR", str(e))

@router.post("/webhooks/provider")
async def api_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    try:
        result = handle_webhook(payload, signature)
        if not result.get("ok"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return success_response(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
