from decimal import Decimal

from app.billing.service_broker_kpi import aggregate_service_broker_kpi


def test_aggregate_service_broker_kpi() -> None:
    events = [
        {"schema_version": "service-broker.acquisition.v1", "expected_cac": "1500"},
        {"schema_version": "service-broker.lead.v1"},
        {"schema_version": "service-broker.lead.v1"},
        {"schema_version": "service-broker.qualification.v1", "qualified": True},
        {"schema_version": "service-broker.qualification.v1", "qualified": False},
        {
            "schema_version": "service-broker.settlement.v1",
            "revenue": "15000",
            "actual_contribution": "3000",
            "supplier_sla_met": True,
            "had_rework": False,
        },
        {
            "schema_version": "service-broker.settlement.v1",
            "revenue": "20000",
            "actual_contribution": "8000",
            "supplier_sla_met": False,
            "had_rework": True,
        },
    ]

    kpi = aggregate_service_broker_kpi(events)
    snapshot = kpi.to_snapshot()

    assert kpi.revenue == Decimal("35000")
    assert kpi.qualified_rate == Decimal("0.5")
    assert kpi.cac == Decimal("750")
    assert kpi.aov == Decimal("17500")
    assert kpi.realized_contribution == Decimal("11000")
    assert kpi.contribution_per_job == Decimal("5500")
    assert kpi.supplier_sla_rate == Decimal("0.5")
    assert kpi.rework_rate == Decimal("0.5")
    assert kpi.jobs_remaining_to_target == 4
    assert snapshot["schema_version"] == "service-broker.kpi.v1"


def test_zero_denominators_are_safe() -> None:
    kpi = aggregate_service_broker_kpi([], target_contribution=Decimal("30000"))

    assert kpi.qualified_rate == 0
    assert kpi.cac == 0
    assert kpi.aov == 0
    assert kpi.contribution_margin == 0
    assert kpi.supplier_sla_rate == 0
    assert kpi.rework_rate == 0
    assert kpi.jobs_remaining_to_target == 0


def test_target_is_complete_when_contribution_reaches_target() -> None:
    kpi = aggregate_service_broker_kpi(
        [
            {
                "schema_version": "service-broker.settlement.v1",
                "revenue": "50000",
                "actual_contribution": "32000",
            }
        ]
    )

    assert kpi.jobs_remaining_to_target == 0
