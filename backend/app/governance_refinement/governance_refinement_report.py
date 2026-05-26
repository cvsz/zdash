from .refinement_service import refinement_snapshot

def governance_report() -> dict:
    return {"report": refinement_snapshot(), "advisory_only": True}
