from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.dependencies import require_permissions
from app.auth.rbac import Permission, has_permission
from app.billing.entitlement_service import require_feature
from app.core.responses import error_response, success_response

from app.enterprise.branding_service import (
    get_branding,
    reset_branding,
    update_branding,
)
from app.enterprise.export_service import (
    create_export_bundle,
    get_export_bundle,
    list_export_bundles,
)
from app.enterprise.license_service import (
    apply_license,
    get_license_status,
    revoke_license,
)
from app.enterprise.onboarding_service import (
    get_customer_health,
    get_checklist,
    mark_step_complete,
    reset_checklist,
)

router = APIRouter(prefix="/api/enterprise", tags=["enterprise"])


class ApplyLicenseRequest(BaseModel):
    license_key: str


class ExportRequest(BaseModel):
    export_type: str = "full"
    include_audit_logs: bool = False
    include_content: bool = True
    include_backtests: bool = False
    include_scheduler: bool = True
    include_secrets: bool = False
    secret_export_confirmation: str | None = None


class OnboardingStepRequest(BaseModel):
    step: str


def _org_id(current_user: Any) -> str:
    return (
        getattr(current_user, "organization_id", None)
        or getattr(current_user, "username", None)
        or "default"
    )


def _ws_id(current_user: Any) -> str | None:
    return getattr(current_user, "workspace_id", None)


@router.get("/status")
def api_status(
    current_user: Any = Depends(require_permissions([Permission.enterprise_read])),
):
    org_id = _org_id(current_user)
    ws_id = _ws_id(current_user)
    return success_response(
        {
            "license": get_license_status(org_id),
            "branding": get_branding(org_id, ws_id),
        }
    )


@router.get("/license")
def api_license_status(
    current_user: Any = Depends(require_permissions([Permission.enterprise_read])),
):
    return success_response(get_license_status(_org_id(current_user)))


@router.post("/license/apply")
def api_license_apply(
    req: ApplyLicenseRequest,
    current_user: Any = Depends(
        require_permissions([Permission.enterprise_license_manage])
    ),
):
    return success_response(apply_license(_org_id(current_user), req.license_key))


@router.post("/license/revoke")
def api_license_revoke(
    current_user: Any = Depends(
        require_permissions([Permission.enterprise_license_manage])
    ),
):
    return success_response(revoke_license(_org_id(current_user)))


@router.get("/branding")
def api_branding(
    current_user: Any = Depends(require_permissions([Permission.enterprise_read])),
):
    return success_response(get_branding(_org_id(current_user), _ws_id(current_user)))


@router.patch("/branding")
def api_branding_patch(
    body: dict,
    current_user: Any = Depends(
        require_permissions([Permission.enterprise_branding_manage])
    ),
):
    return success_response(
        update_branding(_org_id(current_user), _ws_id(current_user), body)
    )


@router.post("/branding/reset")
def api_branding_reset(
    current_user: Any = Depends(
        require_permissions([Permission.enterprise_branding_manage])
    ),
):
    return success_response(reset_branding(_org_id(current_user), _ws_id(current_user)))


@router.get("/exports")
def api_exports(
    current_user: Any = Depends(require_permissions([Permission.enterprise_export])),
):
    return success_response({"exports": list_export_bundles(_org_id(current_user))})


@router.post("/exports")
def api_create_export(
    req: ExportRequest,
    current_user: Any = Depends(require_permissions([Permission.enterprise_export])),
    _f: str = Depends(require_feature("feature.enterprise_export")),
):
    if req.include_secrets:
        if req.secret_export_confirmation != "CONFIRM_SECRET_EXPORT":
            return error_response(
                "SECRET_EXPORT_CONFIRMATION_REQUIRED",
                "Type CONFIRM_SECRET_EXPORT to include secrets in an export.",
            )
        if not has_permission(
            getattr(current_user, "role", "viewer"),
            Permission.enterprise_export_secrets,
        ):
            return error_response(
                "SECRET_EXPORT_DENIED",
                "Missing enterprise_export_secrets permission",
            )

    req_dict = req.model_dump()
    req_dict.pop("secret_export_confirmation", None)
    req_dict["organization_id"] = _org_id(current_user)
    req_dict["workspace_id"] = _ws_id(current_user)

    return success_response(create_export_bundle(req_dict))


@router.get("/exports/{bundle_id}")
def api_export_get(
    bundle_id: str,
    current_user: Any = Depends(require_permissions([Permission.enterprise_export])),
):
    return success_response(get_export_bundle(_org_id(current_user), bundle_id))


@router.get("/onboarding")
def api_onboarding(
    current_user: Any = Depends(require_permissions([Permission.enterprise_read])),
):
    return success_response(get_checklist(_org_id(current_user), _ws_id(current_user)))


@router.post("/onboarding/complete-step")
def api_onboarding_step(
    req: OnboardingStepRequest,
    current_user: Any = Depends(
        require_permissions([Permission.enterprise_onboarding_manage])
    ),
):
    return success_response(
        mark_step_complete(_org_id(current_user), _ws_id(current_user), req.step)
    )


@router.post("/onboarding/reset")
def api_onboarding_reset(
    current_user: Any = Depends(
        require_permissions([Permission.enterprise_onboarding_manage])
    ),
):
    return success_response(
        reset_checklist(_org_id(current_user), _ws_id(current_user))
    )


@router.get("/customer-health")
def api_health(
    current_user: Any = Depends(require_permissions([Permission.enterprise_read])),
):
    return success_response(
        get_customer_health(_org_id(current_user), _ws_id(current_user))
    )
