from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from math import ceil
from typing import Iterable, Mapping


ZERO = Decimal("0")


@dataclass(frozen=True)
class ServiceBrokerKPI:
    revenue: Decimal
    leads: int
    qualified_leads: int
    acquisition_cost: Decimal
    jobs: int
    realized_contribution: Decimal
    supplier_sla_met: int
    supplier_sla_total: int
    rework_jobs: int
    target_contribution: Decimal = Decimal("30000")

    @property
    def qualified_rate(self) -> Decimal:
        return ZERO if self.leads == 0 else Decimal(self.qualified_leads) / Decimal(self.leads)

    @property
    def cac(self) -> Decimal:
        return ZERO if self.leads == 0 else self.acquisition_cost / Decimal(self.leads)

    @property
    def aov(self) -> Decimal:
        return ZERO if self.jobs == 0 else self.revenue / Decimal(self.jobs)

    @property
    def contribution_per_job(self) -> Decimal:
        return ZERO if self.jobs == 0 else self.realized_contribution / Decimal(self.jobs)

    @property
    def contribution_margin(self) -> Decimal:
        return ZERO if self.revenue == 0 else self.realized_contribution / self.revenue

    @property
    def supplier_sla_rate(self) -> Decimal:
        return ZERO if self.supplier_sla_total == 0 else Decimal(self.supplier_sla_met) / Decimal(self.supplier_sla_total)

    @property
    def rework_rate(self) -> Decimal:
        return ZERO if self.jobs == 0 else Decimal(self.rework_jobs) / Decimal(self.jobs)

    @property
    def jobs_remaining_to_target(self) -> int:
        remaining = self.target_contribution - self.realized_contribution
        if remaining <= 0:
            return 0
        per_job = self.contribution_per_job
        if per_job <= 0:
            return 0
        return ceil(remaining / per_job)

    def to_snapshot(self) -> dict[str, str | int]:
        return {
            "schema_version": "service-broker.kpi.v1",
            "revenue": str(self.revenue),
            "leads": self.leads,
            "qualified_leads": self.qualified_leads,
            "qualified_rate": str(self.qualified_rate),
            "acquisition_cost": str(self.acquisition_cost),
            "cac": str(self.cac),
            "jobs": self.jobs,
            "aov": str(self.aov),
            "realized_contribution": str(self.realized_contribution),
            "contribution_per_job": str(self.contribution_per_job),
            "contribution_margin": str(self.contribution_margin),
            "supplier_sla_rate": str(self.supplier_sla_rate),
            "rework_rate": str(self.rework_rate),
            "target_contribution": str(self.target_contribution),
            "jobs_remaining_to_target": self.jobs_remaining_to_target,
        }


def aggregate_service_broker_kpi(events: Iterable[Mapping[str, object]], *, target_contribution: Decimal = Decimal("30000")) -> ServiceBrokerKPI:
    revenue = ZERO
    leads = 0
    qualified_leads = 0
    acquisition_cost = ZERO
    jobs = 0
    realized_contribution = ZERO
    supplier_sla_met = 0
    supplier_sla_total = 0
    rework_jobs = 0

    for event in events:
        schema = str(event.get("schema_version", ""))
        if schema == "service-broker.acquisition.v1":
            acquisition_cost += Decimal(str(event.get("expected_cac", "0")))
        elif schema == "service-broker.lead.v1":
            leads += 1
        elif schema == "service-broker.qualification.v1":
            if bool(event.get("qualified", False)):
                qualified_leads += 1
        elif schema == "service-broker.settlement.v1":
            jobs += 1
            revenue += Decimal(str(event.get("revenue", event.get("amount_paid", "0"))))
            realized_contribution += Decimal(str(event.get("actual_contribution", "0")))
            if "supplier_sla_met" in event:
                supplier_sla_total += 1
                supplier_sla_met += int(bool(event.get("supplier_sla_met")))
            rework_jobs += int(bool(event.get("had_rework", False)))

    return ServiceBrokerKPI(
        revenue=revenue,
        leads=leads,
        qualified_leads=qualified_leads,
        acquisition_cost=acquisition_cost,
        jobs=jobs,
        realized_contribution=realized_contribution,
        supplier_sla_met=supplier_sla_met,
        supplier_sla_total=supplier_sla_total,
        rework_jobs=rework_jobs,
        target_contribution=target_contribution,
    )
