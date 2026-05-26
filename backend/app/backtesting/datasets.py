from __future__ import annotations

import csv
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from app.backtesting.models import Candle


class DatasetProvider:
    def __init__(
        self,
        mock_provider: "MockDatasetProvider | None" = None,
        csv_provider: "CsvDatasetProvider | None" = None,
    ) -> None:
        self._mock_provider = mock_provider or MockDatasetProvider()
        self._csv_provider = csv_provider or CsvDatasetProvider()

    def load(self, dataset: str, symbol: str, timeframe: str) -> list[Candle]:
        if dataset == "mock":
            return self._mock_provider.load(dataset, symbol, timeframe)
        if dataset.startswith("csv:"):
            return self._csv_provider.load(dataset, symbol, timeframe)
        raise ValueError(f"Unsupported dataset: {dataset}")


class MockDatasetProvider:
    def __init__(self, candle_count: int = 360) -> None:
        self._candle_count = max(300, candle_count)

    def load(self, dataset: str, symbol: str, timeframe: str) -> list[Candle]:
        if symbol != "XAUUSD" or timeframe != "M5":
            raise ValueError("mock dataset supports only XAUUSD M5")

        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        out: list[Candle] = []
        price = 2300.0
        for i in range(self._candle_count):
            trend = math.sin(i / 18.0) * 2.8 + math.cos(i / 29.0) * 1.7
            impulse = math.sin(i / 3.5) * 0.7
            drift = trend + impulse
            open_p = price
            close = open_p + drift
            high = max(open_p, close) + abs(math.sin(i / 2.3)) * 1.1 + 0.2
            low = min(open_p, close) - abs(math.cos(i / 2.7)) * 1.1 - 0.2
            vol = 100 + (i % 20) * 6
            candle = Candle(
                timestamp=start + timedelta(minutes=5 * i),
                open=round(open_p, 5),
                high=round(high, 5),
                low=round(low, 5),
                close=round(close, 5),
                volume=float(vol),
            )
            out.append(candle)
            price = close
        return out


class CsvDatasetProvider:
    base_dir = Path(__file__).resolve().parents[2] / "data" / "backtests"

    def load(self, dataset: str, symbol: str, timeframe: str) -> list[Candle]:
        filename = dataset.replace("csv:", "", 1).strip()
        if not filename:
            raise ValueError("CSV dataset name is required")
        if Path(filename).name != filename:
            raise ValueError("Path traversal is not allowed in CSV dataset name")

        file_path = (self.base_dir / filename).resolve()
        safe_base = self.base_dir.resolve()
        if safe_base not in file_path.parents:
            raise ValueError("Path traversal is not allowed")
        if not file_path.exists():
            raise ValueError(f"CSV dataset not found: {filename}")

        candles: list[Candle] = []
        with file_path.open("r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            required = {"timestamp", "open", "high", "low", "close", "volume"}
            if not required.issubset(set(reader.fieldnames or [])):
                raise ValueError("CSV missing required columns")

            for row in _iter_rows(reader):
                timestamp_raw = str(row["timestamp"]).strip().replace("Z", "+00:00")
                candles.append(
                    Candle(
                        timestamp=datetime.fromisoformat(timestamp_raw),
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=float(row.get("volume") or 0),
                    )
                )

        if not candles:
            raise ValueError("CSV dataset contains no candles")
        return candles


def _iter_rows(reader: csv.DictReader) -> Iterable[dict[str, str]]:
    for row in reader:
        # Ignore blank lines and malformed empty rows.
        if not row:
            continue
        if all(str(value).strip() == "" for value in row.values()):
            continue
        yield row
