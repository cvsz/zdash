from .plan_catalog import list_public_plans
from .mock_billing_adapter import MockBillingAdapter
from .entitlement_service import ORG_PLAN
ADAPTER=MockBillingAdapter()
def get_status(organization_id): return {'organization_id':organization_id,'plan':ORG_PLAN.get(organization_id,'free'),'provider':'mock'}
def list_plans(): return list_public_plans()
def start_checkout(organization_id, plan_id): return ADAPTER.create_checkout_session(organization_id,plan_id)
def open_billing_portal(organization_id): return ADAPTER.create_billing_portal_session(organization_id)
def cancel_subscription(organization_id): return {'organization_id':organization_id,'status':'canceled'}
def sync_subscription_from_provider(organization_id): return {'organization_id':organization_id,'status':'active'}
def apply_mock_plan(organization_id, plan_tier): ORG_PLAN[organization_id]=plan_tier; return {'organization_id':organization_id,'plan':plan_tier}
