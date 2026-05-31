import hashlib
from typing import Dict, Any
from sqlalchemy import select
from app.db.session import SessionLocal
from app.enterprise.models import EnterpriseLicense
from app.enterprise.models_enums import LicenseStatus
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def hash_license(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()

def get_license_status(organization_id: str) -> Dict[str, Any]:
    with SessionLocal() as db:
        lic = db.execute(select(EnterpriseLicense).where(EnterpriseLicense.organization_id == organization_id)).scalar()
        if not lic:
            return {"status": "none"}
            
        ret = dict(lic.__dict__)
        ret.pop('_sa_instance_state', None)
        
        # Check expiry
        if lic.expires_at and lic.expires_at < utc_now():
            ret["status"] = LicenseStatus.expired.value
            
        return ret

def apply_license(organization_id: str, license_key: str) -> Dict[str, Any]:
    with SessionLocal() as db:
        lic = db.execute(select(EnterpriseLicense).where(EnterpriseLicense.organization_id == organization_id)).scalar()
        
        # Super simplified validation for demo
        valid = len(license_key) > 5
        if not valid:
            return {"ok": False, "error": "LICENSE_INVALID"}
            
        if not lic:
            lic = EnterpriseLicense(
                organization_id=organization_id,
                license_key_hash=hash_license(license_key),
                status=LicenseStatus.active,  # type: ignore[arg-type]
                tier="enterprise"
            )
            db.add(lic)
        else:
            lic.license_key_hash = hash_license(license_key)  # type: ignore[assignment]

            lic.status = LicenseStatus.active  # type: ignore[assignment]
            lic.updated_at = utc_now()  # type: ignore[assignment]
            
        db.commit()
    return {"ok": True, "status": "active"}

def revoke_license(organization_id: str) -> Dict[str, Any]:
    with SessionLocal() as db:
        lic = db.execute(select(EnterpriseLicense).where(EnterpriseLicense.organization_id == organization_id)).scalar()
        if lic:
            lic.status = LicenseStatus.revoked  # type: ignore[assignment]
            lic.updated_at = utc_now()  # type: ignore[assignment]
            db.commit()
    return {"ok": True, "status": "revoked"}

def validate_license(organization_id: str) -> bool:
    status = get_license_status(organization_id)
    return status.get("status") == "active"
