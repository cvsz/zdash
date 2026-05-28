from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select

from app.billing.models import Invoice
from app.core.events import event_bus
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


def _invoice_to_dict(inv: Invoice) -> dict[str, Any]:
    return {
        "id": inv.id,
        "organization_id": inv.organization_id,
        "provider": inv.provider,
        "provider_invoice_id": inv.provider_invoice_id,
        "status": inv.status,
        "amount_due": float(inv.amount_due) if inv.amount_due is not None else 0.0,
        "amount_paid": float(inv.amount_paid) if inv.amount_paid is not None else 0.0,
        "currency": inv.currency,
        "hosted_invoice_url": inv.hosted_invoice_url,
        "invoice_pdf_url": inv.invoice_pdf_url,
        "created_at": inv.created_at.isoformat() if isinstance(inv.created_at, datetime) else None,
        "due_at": inv.due_at.isoformat() if isinstance(inv.due_at, datetime) else None,
        "paid_at": inv.paid_at.isoformat() if isinstance(inv.paid_at, datetime) else None,
    }


def get_invoices(organization_id: str, limit: int = 50) -> list[dict[str, Any]]:
    """Return invoices for an organization, most-recent first."""
    with SessionLocal() as db:
        invoices = (
            db.execute(
                select(Invoice)
                .where(Invoice.organization_id == organization_id)
                .order_by(Invoice.created_at.desc())
                .limit(max(1, min(limit, 200)))
            )
            .scalars()
            .all()
        )
        result = [_invoice_to_dict(inv) for inv in invoices]

    event_bus.emit(
        "billing.invoice.synced",
        "billing.invoice_service",
        f"Invoice list fetched for org {organization_id}",
        {"organization_id": organization_id, "count": len(result)},
    )
    return result


def create_mock_invoice(
    organization_id: str,
    amount_due: float = 0.0,
    currency: str = "USD",
) -> dict[str, Any]:
    """Create a mock invoice record for testing purposes."""
    import uuid

    with SessionLocal() as db:
        inv = Invoice(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            provider="mock",
            provider_invoice_id=f"inv_mock_{uuid.uuid4().hex[:8]}",
            status="paid",
            amount_due=amount_due,
            amount_paid=amount_due,
            currency=currency,
            hosted_invoice_url="https://mock-billing.test/invoice/view",
            invoice_pdf_url="https://mock-billing.test/invoice/pdf",
        )
        db.add(inv)
        db.commit()
        return _invoice_to_dict(inv)
