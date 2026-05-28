from typing import Dict, Any, Optional
from sqlalchemy import select
from app.db.session import SessionLocal
from app.enterprise.models import BrandingSettings
from app.core.config import settings
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def get_branding(organization_id: str, workspace_id: Optional[str] = None) -> Dict[str, Any]:
    with SessionLocal() as db:
        query = select(BrandingSettings).where(BrandingSettings.organization_id == organization_id)
        if workspace_id:
            query = query.where(BrandingSettings.workspace_id == workspace_id)
        
        brand = db.execute(query).scalar()
        if brand:
            ret = dict(brand.__dict__)
            ret.pop('_sa_instance_state', None)
            return ret
            
        return {
            "brand_name": settings.default_brand_name,
            "logo_url": settings.default_brand_logo_url,
            "primary_color": settings.default_brand_primary_color,
            "accent_color": settings.default_brand_accent_color,
        }

def update_branding(organization_id: str, workspace_id: Optional[str], patch: Dict[str, Any]) -> Dict[str, Any]:
    with SessionLocal() as db:
        query = select(BrandingSettings).where(BrandingSettings.organization_id == organization_id)
        if workspace_id:
            query = query.where(BrandingSettings.workspace_id == workspace_id)
            
        brand = db.execute(query).scalar()
        
        # Validation
        for k in ["primary_color", "accent_color"]:
            if k in patch and patch[k] and not patch[k].startswith("#"):
                return {"ok": False, "error": "Invalid color format"}
                
        # Basic sanitization
        for k, v in patch.items():
            if isinstance(v, str) and ("<script>" in v.lower() or "javascript:" in v.lower()):
                return {"ok": False, "error": "Invalid content"}
        
        if not brand:
            brand = BrandingSettings(
                organization_id=organization_id,
                workspace_id=workspace_id,
                brand_name=patch.get("brand_name", settings.default_brand_name),
                logo_url=patch.get("logo_url", settings.default_brand_logo_url),
                primary_color=patch.get("primary_color", settings.default_brand_primary_color),
                accent_color=patch.get("accent_color", settings.default_brand_accent_color),
                support_email=patch.get("support_email"),
                custom_domain=patch.get("custom_domain")
            )
            db.add(brand)
        else:
            for k, v in patch.items():
                if hasattr(brand, k) and k != "id" and k != "organization_id":
                    setattr(brand, k, v)
            brand.updated_at = utc_now()
            
        db.commit()
    return {"ok": True}

def reset_branding(organization_id: str, workspace_id: Optional[str] = None) -> Dict[str, Any]:
    with SessionLocal() as db:
        query = select(BrandingSettings).where(BrandingSettings.organization_id == organization_id)
        if workspace_id:
            query = query.where(BrandingSettings.workspace_id == workspace_id)
            
        brand = db.execute(query).scalar()
        if brand:
            db.delete(brand)
            db.commit()
    return {"ok": True}
