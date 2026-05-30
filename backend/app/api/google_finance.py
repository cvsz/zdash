from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.responses import success_response
from app.market_data.google_finance_beta import overview_payload, search_url, section_url

router = APIRouter(prefix="/api/integrations/google-finance", tags=["integrations", "google-finance"])


@router.get("/status")
def status():
    return success_response(
        {
            "enabled": True,
            "mode": "read_only_link_adapter",
            "provider": "google_finance_beta",
            "scraping_enabled": False,
            "live_quote_api": False,
            "disclaimer": "Simulation support only. Not financial advice.",
        }
    )


@router.get("/overview")
def overview():
    return success_response(overview_payload())


@router.get("/sections/{section}")
def section(section: str):
    return success_response({"section": section, "url": section_url(section)})


@router.get("/search")
def search(q: str = Query(..., min_length=1, max_length=80)):
    return success_response({"query": q, "url": search_url(q)})
