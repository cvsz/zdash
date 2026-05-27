from pathlib import Path

import pytest

from app.backtesting.datasets import (
    CsvDatasetProvider,
    DatasetProvider,
    MockDatasetProvider,
)


def test_mock_dataset_returns_valid_candles() -> None:
    candles = MockDatasetProvider().load("mock", "XAUUSD", "M5")
    assert len(candles) >= 300
    assert candles[0].close > 0
    assert candles[10].high >= candles[10].low


def test_mock_dataset_is_deterministic() -> None:
    first_run = MockDatasetProvider().load("mock", "XAUUSD", "M5")
    second_run = MockDatasetProvider().load("mock", "XAUUSD", "M5")
    assert [item.close for item in first_run[:20]] == [
        item.close for item in second_run[:20]
    ]


def test_csv_path_traversal_is_rejected() -> None:
    provider = CsvDatasetProvider()
    with pytest.raises(ValueError, match="Path traversal"):
        provider.load("csv:../../etc/passwd", "XAUUSD", "M5")


def test_missing_csv_returns_clean_error() -> None:
    provider = CsvDatasetProvider()
    with pytest.raises(ValueError, match="CSV dataset not found"):
        provider.load("csv:missing_file.csv", "XAUUSD", "M5")


def test_csv_dataset_loads_known_sample() -> None:
    provider = DatasetProvider()
    candles = provider.load("csv:sample_xauusd_m5.csv", "XAUUSD", "M5")
    assert len(candles) == 3
    assert candles[0].open == 2300.0
    assert candles[-1].close == 2301.2
    assert Path(CsvDatasetProvider.base_dir / "sample_xauusd_m5.csv").exists()
