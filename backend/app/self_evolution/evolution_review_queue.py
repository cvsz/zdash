from .change_proposal_service import change_proposals

def review_queue() -> dict:
    return {"queue": change_proposals()["proposals"], "status": "pending_human_review"}
