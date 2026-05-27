from .models import EntitlementDecision
from .plan_catalog import get_plan

ORDER = ["free", "starter", "pro", "enterprise"]
ORG_PLAN = {}


def get_plan_for_org(organization_id):
    return get_plan(ORG_PLAN.get(organization_id, "free"))


def check_feature(organization_id, feature):
    p = get_plan_for_org(organization_id)
    allowed = feature in p.features
    return EntitlementDecision(
        allowed=allowed,
        feature=feature,
        reason="ok" if allowed else "FEATURE_NOT_ENTITLED",
        plan_tier=p.tier.value,
    )


def check_quota(organization_id, workspace_id, metric, increment=1):
    return EntitlementDecision(
        True, metric, "ok", get_plan_for_org(organization_id).tier.value
    )


def require_feature(feature):
    def _dep():
        return feature

    return _dep


def require_quota(metric, increment=1):
    def _dep():
        return metric

    return _dep
