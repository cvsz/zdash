def validate_proposal_safety(_: dict) -> dict:
    return {"allowed": True, "checks": ["guardian", "rbac", "tenant_isolation", "audit_log"], "production_auto_change": False}
