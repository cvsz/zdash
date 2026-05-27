from collections import defaultdict

USAGE: defaultdict[tuple[str, str, str], int] = defaultdict(int)


def record_usage(organization_id, workspace_id, metric, quantity=1, **kwargs):
    USAGE[(organization_id, workspace_id, metric)] += quantity
    return {"ok": True}


def get_metric_summary(organization_id, workspace_id, metric):
    return {
        "organization_id": organization_id,
        "workspace_id": workspace_id,
        "metric": metric,
        "used": USAGE[(organization_id, workspace_id, metric)],
    }


def get_usage_summary(organization_id, workspace_id=None):
    out = []
    for (org, ws, m), v in USAGE.items():
        if org == organization_id and (workspace_id is None or ws == workspace_id):
            out.append({"workspace_id": ws, "metric": m, "used": v})
    return out


def reset_period_if_needed():
    return {"ok": True}
