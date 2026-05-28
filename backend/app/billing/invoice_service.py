from typing import List, Dict, Any
from sqlalchemy import select
from app.db.session import SessionLocal
from app.billing.models import Invoice

def get_invoices(organization_id: str) -> List[Dict[str, Any]]:
    with SessionLocal() as db:
        invoices = db.execute(
            select(Invoice)
            .where(Invoice.organization_id == organization_id)
            .order_by(Invoice.created_at.desc())
        ).scalars().all()
        
        return [
            {
                "id": inv.id,
                "amount_due": float(inv.amount_due) if inv.amount_due else 0,
                "amount_paid": float(inv.amount_paid) if inv.amount_paid else 0,
                "currency": inv.currency,
                "status": inv.status,
                "hosted_invoice_url": inv.hosted_invoice_url,
                "invoice_pdf_url": inv.invoice_pdf_url,
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
                "due_at": inv.due_at.isoformat() if inv.due_at else None,
                "paid_at": inv.paid_at.isoformat() if inv.paid_at else None
            }
            for inv in invoices
        ]
