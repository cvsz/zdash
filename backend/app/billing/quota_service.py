from .entitlement_service import check_quota
from .usage_meter import record_usage


def can_consume(organization_id, workspace_id, metric, quantity=1):
    return check_quota(organization_id, workspace_id, metric, quantity)


def consume(
    organization_id, workspace_id, metric, quantity=1, source=None, resource_id=None
):
    d = can_consume(organization_id, workspace_id, metric, quantity)
    if d.allowed:
        record_usage(
            organization_id,
            workspace_id,
            metric,
            quantity,
            source=source,
            resource_id=resource_id,
        )
    return d


def get_quota_status(organization_id, workspace_id=None):
    return {"items": []}
