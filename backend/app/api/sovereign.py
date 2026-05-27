from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from app.sovereign.models import (
    RegionRecord,
    DataResidencyRule,
    SovereignDeploymentProfile,
    KMSKeyRecord,
    PolicyBundle,
)
from app.sovereign.region_registry import RegionRegistry
from app.sovereign.residency_engine import ResidencyEngine
from app.sovereign.sovereign_profiles import SovereignProfileService
from app.sovereign.key_management_service import KeyManagementService
from app.sovereign.policy_bundle_service import PolicyBundleService
from app.sovereign.compliance_dashboard import SovereignComplianceDashboard


def ts():
    return datetime.now(timezone.utc).isoformat()


def ok(data):
    return {"ok": True, "data": data, "error": None, "timestamp": ts()}


router = APIRouter(prefix="/api/sovereign", tags=["sovereign"])
regions = RegionRegistry()
residency = ResidencyEngine()
profiles = SovereignProfileService()
kms = KeyManagementService()
bundles = PolicyBundleService()
dashboard = SovereignComplianceDashboard(regions, residency, kms, bundles)


class EvalReq(BaseModel):
    source_region: str = "local"
    target_region: str = "local"
    resource_type: str = "generic"
    organization_id: str = "default"


@router.get("/status")
def status():
    return ok(dashboard.get_status())


@router.get("/regions")
def list_regions():
    return ok([r.model_dump() for r in regions.list_regions()])


@router.post("/regions")
def create_region(region: RegionRecord):
    return ok(regions.register_region(region).model_dump())


@router.get("/residency/rules")
def list_rules():
    return ok([r.model_dump() for r in residency.list_rules()])


@router.post("/residency/rules")
def create_rule(rule: DataResidencyRule):
    return ok(residency.create_rule(rule).model_dump())


@router.post("/residency/evaluate")
def evaluate(req: EvalReq):
    return ok(
        residency.evaluate_transfer(
            req.source_region,
            req.target_region,
            req.resource_type,
            {"organization_id": req.organization_id},
        ).model_dump()
    )


@router.post("/residency/enforce")
def enforce(req: EvalReq):
    return ok(
        residency.enforce_residency(
            "transfer",
            req.resource_type,
            req.target_region,
            {
                "organization_id": req.organization_id,
                "source_region": req.source_region,
            },
        ).model_dump()
    )


@router.get("/profiles")
def list_profiles():
    return ok([p.model_dump() for p in profiles.list_profiles()])


@router.post("/profiles")
def create_profile(profile: SovereignDeploymentProfile):
    return ok(profiles.create_profile(profile).model_dump())


@router.post("/profiles/{profile_id}/activate")
def activate(profile_id: str):
    return ok(profiles.activate_profile(profile_id).model_dump())


@router.post("/profiles/{profile_id}/disable")
def disable(profile_id: str):
    return ok(profiles.disable_profile(profile_id).model_dump())


@router.get("/kms/status")
def kms_status():
    return ok(kms.get_kms_status())


class KeyReq(BaseModel):
    id: str
    organization_id: str = "default"
    key_ref: str


@router.post("/kms/register-key-ref")
def register_key(req: KeyReq):
    return ok(
        kms.register_key_ref(
            KMSKeyRecord(
                id=req.id,
                organization_id=req.organization_id,
                key_ref_hash=KeyManagementService.hash_ref(req.key_ref),
            )
        ).model_dump()
    )


@router.post("/kms/test")
def test_kms():
    return ok(kms.test_kms_connection())


@router.get("/policy-bundles")
def list_bundles():
    return ok([b.model_dump() for b in bundles.list_bundles()])


@router.post("/policy-bundles")
def create_bundle(bundle: PolicyBundle):
    return ok(bundles.create_bundle(bundle).model_dump())


@router.get("/compliance/dashboard")
def compliance_dashboard():
    return ok(dashboard.generate_report())


@router.get("/compliance/report")
def compliance_report():
    return ok(dashboard.generate_report())
