from .models import ImprovementProposal

def scan_improvements() -> list[ImprovementProposal]:
    return [ImprovementProposal(id="imp-1", title="Increase test coverage on API boundaries", confidence=0.71)]
