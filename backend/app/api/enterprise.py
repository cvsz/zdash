from fastapi import APIRouter, Depends
from typing import Any
from pydantic import BaseModel

from app.core.responses import success_response, error_response
from app.billing.entitlement_service import require_feature
from app.auth.dependencies import require_permissions
from app.auth.rbac import Permission

from app.enterprise.license_service import (
    get_license_status,
    apply_license,
    revoke_license,
)
from app.enterprise.branding_service import (
    get_branding,
    update_branding,
    reset_branding,
)
from app.enterprise.export_service import (
    list_export_bundles,
    create_export_bundle,
    get_export_bundle,
)
from app.enterprise.onboarding_service import (
    get_checklist,
    mark_step_complete,
    reset_checklist,
    get_customer_health,
)

router = APIRouter()

class ApplyLicenseRequest(BaseModel):
    license_key: str

class ExportRequest(BaseModel):
    export_type: str = "full"
    include_audit_logs: bool = False
    include_content: bool = True
    include_backtests: bool = False
    include_scheduler: bool = True
    include_secrets: bool = False

class OnboardingStepRequest(BaseModel):
    step: str

@router.get("/status")
def api_status(current_user: Any = Depends(require_permissions([Permission.enterprise_read]))):
    ws_id = current_user.workspace_id if hasattr(current_user, "workspace_id") else None
    return success_response(
        {
            "license": get_license_status(current_user.organization_id),
            "branding": get_branding(current_user.organization_id, ws_id),
        }
    )

@router.get("/license")
def api_license_status(current_user: Any = Depends(require_permissions([Permission.enterprise_read]))):
    return success_response(get_license_status(current_user.organization_id))

@router.post("/license/apply")
def api_license_apply(req: ApplyLicenseRequest, current_user: Any = Depends(require_permissions([Permission.enterprise_license_manage]))):
    return success_response(apply_license(current_user.organization_id, req.license_key))

@router.post("/license/revoke")
def api_license_revoke(current_user: Any = Depends(require_permissions([Permission.enterprise_license_manage]))):
    return success_response(revoke_license(current_user.organization_id))

@router.get("/branding")
def api_branding(current_user: Any = Depends(require_permissions([Permission.enterprise_read]))):
    ws_id = current_user.workspace_id if hasattr(current_user, "workspace_id") else None
    return success_response(get_branding(current_user.organization_id, ws_id))

@router.patch("/branding")
def api_branding_patch(body: dict, current_user: Any = Depends(require_permissions([Permission.enterprise_branding_manage]))):
    ws_id = current_user.workspace_id if hasattr(current_user, "workspace_id") else None
    return success_response(update_branding(current_user.organization_id, ws_id, body))

@router.post("/branding/reset")
def api_branding_reset(current_user: Any = Depends(require_permissions([Permission.enterprise_branding_manage]))):
    ws_id = current_user.workspace_id if hasattr(current_user, "workspace_id") else None
    return success_response(reset_branding(current_user.organization_id, ws_id))

@router.get("/exports")
def api_exports(current_user: Any = Depends(require_permissions([Permission.enterprise_export]))):
    return success_response({"exports": list_export_bundles(current_user.organization_id)})

@router.post("/exports")
def api_create_export(
    req: ExportRequest, 
    current_user: Any = Depends(require_permissions([Permission.enterprise_export])),
    _f: str = Depends(require_feature("feature.enterprise_export"))
):
    if req.include_secrets:
        # Check specific permission for secret export
        if not hasattr(current_user, "permissions") or Permission.enterprise_export_secrets not in current_user.permissions:
            return error_response("SECRET_EXPORT_DENIED", "Missing enterprise_export_secrets permission")

    ws_id = current_user.workspace_id if hasattr(current_user, "workspace_id") else None
    
    req_dict = req.model_dump()
    req_dict["organization_id"] = current_user.organization_id
    req_dict["workspace_id"] = ws_id
    
    return success_response(create_export_bundle(req_dict))

@router.get("/exports/{bundle_id}")
def api_export_get(bundle_id: str, current_user: Any = Depends(require_permissions([Permission.enterprise_export]))):
    return success_response(get_export_bundle(current_user.organization_id, bundle_id))

@router.get("/onboarding")
def api_onboarding(current_user: Any = Depends(require_permissions([Permission.enterprise_read]))):
    ws_id = current_user.workspace_id if hasattr(current_user, "workspace_id") else None
    return success_response(get_checklist(current_user.organization_id, ws_id))

@router.post("/onboarding/complete-step")
def api_onboarding_step(req: OnboardingStepRequest, current_user: Any = Depends(require_permissions([Permission.enterprise_onboarding_manage]))):
    ws_id = current_user.workspace_id if hasattr(current_user, "workspace_id") else None
    return success_response(mark_step_complete(current_user.organization_id, ws_id, req.step))

@router.post("/onboarding/reset")
def api_onboarding_reset(current_user: Any = Depends(require_permissions([Permission.enterprise_onboarding_manage]))):
    ws_id = current_user.workspace_id if hasattr(current_user, "workspace_id") else None
    return success_response(reset_checklist(current_user.organization_id, ws_id))

@router.get("/customer-health")
def api_health(current_user: Any = Depends(require_permissions([Permission.enterprise_read]))):
    ws_id = current_user.workspace_id if hasattr(current_user, "workspace_id") else None
    return success_response(get_customer_health(current_user.organization_id, ws_id))
