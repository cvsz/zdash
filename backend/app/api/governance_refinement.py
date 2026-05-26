from fastapi import APIRouter
from app.core.responses import ok
from app.governance_refinement.governance_refinement_report import governance_report

router = APIRouter(prefix="/api/governance-refinement", tags=["governance-refinement"])

@router.get("/report")
def report():
    return ok(governance_report())
