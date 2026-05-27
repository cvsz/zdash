from .improvement_scanner import scan_improvements


def change_proposals() -> dict:
    return {
        "proposals": [p.model_dump() for p in scan_improvements()],
        "auto_apply": False,
    }
