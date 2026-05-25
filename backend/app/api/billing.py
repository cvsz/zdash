from fastapi import APIRouter, Depends, Header
from app.core.responses import ok
from app.core.auth import get_current_user
from app.billing.subscription_service import get_status, list_plans, start_checkout, open_billing_portal, cancel_subscription, apply_mock_plan
from app.billing.usage_meter import get_usage_summary, get_metric_summary
from app.billing.invoice_service import list_invoices
router=APIRouter(prefix='/api/billing',tags=['billing'])

def _org(org_id: str|None): return org_id or 'default-org'
@router.get('/status')
def billing_status(user=Depends(get_current_user), x_organization_id: str|None = Header(default=None)): return ok(get_status(_org(x_organization_id)))
@router.get('/plans')
def plans(user=Depends(get_current_user)): return ok({'plans':[p.__dict__ for p in list_plans()]})
@router.get('/subscription')
def subscription(user=Depends(get_current_user), x_organization_id: str|None = Header(default=None)): return ok(get_status(_org(x_organization_id)))
@router.post('/checkout')
def checkout(body:dict,user=Depends(get_current_user), x_organization_id: str|None = Header(default=None)): return ok(start_checkout(_org(x_organization_id),body.get('plan_id','free')))
@router.post('/portal')
def portal(user=Depends(get_current_user), x_organization_id: str|None = Header(default=None)): return ok(open_billing_portal(_org(x_organization_id)))
@router.post('/cancel')
def cancel(user=Depends(get_current_user), x_organization_id: str|None = Header(default=None)): return ok(cancel_subscription(_org(x_organization_id)))
@router.post('/mock/apply-plan')
def mock_apply(body:dict,user=Depends(get_current_user), x_organization_id: str|None = Header(default=None)): return ok(apply_mock_plan(_org(x_organization_id),body.get('plan_tier','free')))
@router.get('/usage')
def usage(user=Depends(get_current_user), x_organization_id: str|None = Header(default=None)): return ok({'usage':get_usage_summary(_org(x_organization_id))})
@router.get('/usage/{metric}')
def usage_metric(metric:str,user=Depends(get_current_user), x_organization_id: str|None = Header(default=None), x_workspace_id: str|None = Header(default=None)): return ok(get_metric_summary(_org(x_organization_id),x_workspace_id or 'default',metric))
@router.get('/invoices')
def invoices(user=Depends(get_current_user), x_organization_id: str|None = Header(default=None)): return ok({'invoices':list_invoices(_org(x_organization_id))})
@router.post('/webhooks/provider')
def webhooks(body:dict): return ok({'received':True,'payload':body})
