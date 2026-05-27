from .models import BrandingSettings
from typing import Any

_BRANDS: dict[tuple[str, str], dict[str, Any]] = {}
def get_branding(organization_id,workspace_id): return _BRANDS.get((organization_id,workspace_id),BrandingSettings(organization_id,workspace_id).__dict__)
def update_branding(organization_id,workspace_id,patch):
    b=get_branding(organization_id,workspace_id); b.update({k:v for k,v in patch.items() if '<script' not in str(v).lower()}); _BRANDS[(organization_id,workspace_id)]=b; return b
def reset_branding(organization_id,workspace_id): _BRANDS.pop((organization_id,workspace_id),None); return get_branding(organization_id,workspace_id)
