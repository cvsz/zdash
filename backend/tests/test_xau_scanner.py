from app.trading.models import ScannerResult
from app.trading.xau_scanner import XAUScanner


def test_scan_returns_scanner_result() -> None:
    scanner = XAUScanner()
    result = scanner.scan(symbol="XAUUSD", timeframe="M5")

    assert isinstance(result, ScannerResult)
    assert result.symbol == "XAUUSD"
    assert result.timeframe == "M5"
    assert result.candles_analyzed >= 300


def test_scan_includes_latest_signal() -> None:
    scanner = XAUScanner()
    result = scanner.scan()

    assert result.latest_signal is not None
    assert result.latest_signal.symbol == "XAUUSD"
    assert result.latest_signal.direction in {"buy", "sell", "hold"}


def test_scan_includes_ai_summary() -> None:
    scanner = XAUScanner()
    result = scanner.scan()

    assert result.ai_summary
    assert "Simulation only" in result.ai_summary
