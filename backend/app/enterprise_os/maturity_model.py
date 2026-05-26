def policy_maturity_score(scores: list[int]) -> float:
    return round(sum(scores) / len(scores), 2) if scores else 0.0
