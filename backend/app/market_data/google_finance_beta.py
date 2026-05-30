from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import quote

GOOGLE_FINANCE_BETA_BASE_URL = "https://www.google.com/finance/beta"
SUPPORTED_SECTIONS = ("home", "us", "europe", "asia", "currencies", "crypto", "futures")


@dataclass(frozen=True)
class FinanceInstrument:
    symbol: str
    name: str
    asset_class: str
    region: str
    query_hint: str


DEFAULT_WATCHLIST: tuple[FinanceInstrument, ...] = (
    FinanceInstrument(".DJI", "Dow Jones", "index", "US", "Dow Jones"),
    FinanceInstrument(".INX", "S&P 500", "index", "US", "S&P 500"),
    FinanceInstrument(".IXIC", "Nasdaq", "index", "US", "Nasdaq"),
    FinanceInstrument("RUT", "Russell 2000", "index", "US", "Russell 2000"),
    FinanceInstrument("VIX", "VIX", "index", "US", "VIX"),
    FinanceInstrument("XAUUSD", "Gold / US Dollar", "commodity", "Futures", "Gold"),
    FinanceInstrument("BTC", "Bitcoin", "crypto", "Crypto", "Bitcoin BTC"),
    FinanceInstrument("ETH", "Ether", "crypto", "Crypto", "Ether ETH"),
)


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def section_url(section: str = "home") -> str:
    normalized = section.strip().lower() or "home"
    if normalized not in SUPPORTED_SECTIONS:
        normalized = "home"
    if normalized == "home":
        return GOOGLE_FINANCE_BETA_BASE_URL
    return f"{GOOGLE_FINANCE_BETA_BASE_URL}/{normalized}"


def search_url(query: str) -> str:
    cleaned = " ".join(query.strip().split())
    if not cleaned:
        return GOOGLE_FINANCE_BETA_BASE_URL
    return f"{GOOGLE_FINANCE_BETA_BASE_URL}/search?q={quote(cleaned)}"


def instrument_payload(item: FinanceInstrument) -> dict[str, str]:
    return {
        "symbol": item.symbol,
        "name": item.name,
        "asset_class": item.asset_class,
        "region": item.region,
        "google_finance_url": search_url(item.query_hint),
    }


def overview_payload() -> dict[str, object]:
    return {
        "provider": "google_finance_beta",
        "mode": "read_only_link_adapter",
        "scraping_enabled": False,
        "base_url": GOOGLE_FINANCE_BETA_BASE_URL,
        "sections": [
            {"id": section, "url": section_url(section)}
            for section in SUPPORTED_SECTIONS
        ],
        "watchlist": [instrument_payload(item) for item in DEFAULT_WATCHLIST],
        "warnings": [
            "No unofficial Google Finance private endpoint is called.",
            "Links open Google Finance Beta for human review.",
            "This integration is not financial advice and does not execute trades.",
        ],
        "timestamp": utc_timestamp(),
    }
