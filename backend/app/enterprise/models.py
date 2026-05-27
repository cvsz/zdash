from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class BrandingSettings:
    organization_id: str
    workspace_id: str
    brand_name: str = "zDash"
    logo_url: str = ""
    primary_color: str = "#7c3aed"
    accent_color: str = "#22c55e"
    support_email: str = ""
    custom_domain: str = ""
    metadata: dict = field(default_factory=dict)
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
