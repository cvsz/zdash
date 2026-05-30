from __future__ import annotations

from app.api import google_finance


def assert_envelope(payload: dict) -> None:
    assert set(payload.keys()) == {"ok", "data", "error", "timestamp"}


def test_google_finance_status() -> None:
    body = google_finance.status()
    assert_envelope(body)
    assert body["ok"] is True
    assert body["data"]["enabled"] is True
    assert body["data"]["mode"] == "read_only_link_adapter"
    assert body["data"]["scraping_enabled"] is False


def test_google_finance_overview() -> None:
    body = google_finance.overview()
    assert_envelope(body)
    data = body["data"]
    assert data["provider"] == "google_finance_beta"
    assert data["mode"] == "read_only_link_adapter"
    assert data["scraping_enabled"] is False
    assert len(data["sections"]) >= 3
    assert len(data["watchlist"]) >= 1
    assert len(data["warnings"]) >= 1


def test_google_finance_section_default() -> None:
    body = google_finance.section("us")
    assert_envelope(body)
    assert "google.com/finance/beta/us" in body["data"]["url"]


def test_google_finance_section_home() -> None:
    body = google_finance.section("home")
    assert_envelope(body)
    assert body["data"]["url"] == "https://www.google.com/finance/beta"


def test_google_finance_search() -> None:
    body = google_finance.search("AAPL")
    assert_envelope(body)
    assert body["data"]["query"] == "AAPL"
    assert "search?q=AAPL" in body["data"]["url"]


def test_google_finance_search_encoded() -> None:
    body = google_finance.search("S&P 500")
    assert_envelope(body)
    assert body["data"]["query"] == "S&P 500"
    assert "q=S%26P%20500" in body["data"]["url"]
