from .enterprise_state_service import enterprise_state
from .operating_model_service import operating_model_snapshot

def enterprise_os_report() -> dict:
    return {"model": operating_model_snapshot(), "state": enterprise_state()}
