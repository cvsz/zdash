from .governance_drift import governance_drift
from .policy_maturity import maturity


def refinement_snapshot() -> dict:
    return {"maturity": maturity(), "drift": governance_drift()}
