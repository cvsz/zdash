from .horizon_scanner import scan_horizon


def horizon_report() -> dict:
    return {"scan": scan_horizon(), "confidence_band": "medium"}
