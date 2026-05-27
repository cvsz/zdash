from .models import (
    DataResidencyRule,
    ResidencyDecision,
    ResidencyEnforcementMode,
    DataRegion,
)


class ResidencyEngine:
    def __init__(self):
        self._rules = []
        self._decisions = []

    def list_rules(self):
        return self._rules

    def create_rule(self, rule: DataResidencyRule):
        self._rules.append(rule)
        return rule

    def update_rule(self, rule_id: str, **fields):
        for r in self._rules:
            if r.id == rule_id:
                for k, v in fields.items():
                    setattr(r, k, v)
                return r
        return None

    def evaluate_transfer(
        self, source_region, target_region, resource_type, tenant_context
    ):
        blocked = any(
            target_region in r.disallowed_regions
            for r in self._rules
            if r.organization_id == tenant_context.get("organization_id")
        )
        decision = ResidencyDecision(
            allowed=not blocked,
            source_region=DataRegion(source_region),
            target_region=DataRegion(target_region),
            resource_type=resource_type,
            reason="blocked by rule" if blocked else "allowed",
            enforcement_mode=ResidencyEnforcementMode.fail_closed,
            matched_rules=[r.id for r in self._rules],
        )
        self._decisions.append(decision)
        return decision

    def enforce_residency(self, action, resource_type, target_region, tenant_context):
        return self.evaluate_transfer(
            tenant_context.get("source_region", "local"),
            target_region,
            resource_type,
            tenant_context,
        )

    def explain_decision(self):
        return self._decisions[-1] if self._decisions else None
