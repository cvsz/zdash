from dataclasses import dataclass


@dataclass
class TenantContext:
    organization_id: str
    workspace_id: str
    user_id: str | None = None
    user_role: str = "viewer"
    source: str = "default"
