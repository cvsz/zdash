from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field


class ReconciliationReport(BaseModel):
    checked_at: datetime
    local_positions: int
    venue_positions: int
    ghost_orders: list[str] = Field(default_factory=list)
    missing_orders: list[str] = Field(default_factory=list)
    healthy: bool


class ReconciliationEngine:
    """Detects divergence between locally tracked orders/positions and the venue.

    Ghost order: tracked locally but unknown to the venue (never filled/cancelled).
    Missing order: known to the venue but absent from the local ledger.
    """

    def __init__(self, max_age: timedelta = timedelta(minutes=5)) -> None:
        self.max_age = max_age

    def reconcile(
        self,
        local_orders: dict[str, dict[str, Any]],
        venue_order_ids: set[str],
        now: datetime | None = None,
    ) -> ReconciliationReport:
        checked_at = now or datetime.now(UTC)

        ghost_orders: list[str] = []
        for order_id, order in sorted(local_orders.items()):
            if order_id in venue_order_ids:
                continue
            created_at = order.get("created_at")
            # Fail closed: orders without a parseable timestamp are ghosts immediately.
            stale = (
                isinstance(created_at, datetime)
                and (checked_at - created_at) > self.max_age
            )
            if stale or not isinstance(created_at, datetime):
                ghost_orders.append(order_id)

        missing_orders = sorted(venue_order_ids - local_orders.keys())

        return ReconciliationReport(
            checked_at=checked_at,
            local_positions=len(local_orders),
            venue_positions=len(venue_order_ids),
            ghost_orders=ghost_orders,
            missing_orders=missing_orders,
            healthy=not ghost_orders and not missing_orders,
        )
