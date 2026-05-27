def schema_evolution_proposals() -> list[dict]:
    return [
        {"proposal": "add proposal_assumptions column", "safety": "backward-compatible"}
    ]
