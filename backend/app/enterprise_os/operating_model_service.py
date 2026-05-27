from .capability_map import default_capability_map
from .operating_cadence import cadence_cycles


def operating_model_snapshot() -> dict:
    return {
        "capabilities": [c.model_dump() for c in default_capability_map()],
        "cadence": cadence_cycles(),
        "dry_run": True,
        "requires_approval": True,
    }
