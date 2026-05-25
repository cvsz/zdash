from __future__ import annotations

import csv
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.backtesting.models import Candle


class DatasetProvider:
    def load(self, dataset: str, symbol: str, timeframe: str) -> list[Candle]:
        if dataset == "mock":
            return MockDatasetProvider().load(dataset, symbol, timeframe)
        if dataset.startswith("csv:"):
            return CsvDatasetProvider().load(dataset, symbol, timeframe)
        raise ValueError(f"Unsupported dataset: {dataset}")


class MockDatasetProvider:
    def load(self, dataset: str, symbol: str, timeframe: str) -> list[Candle]:
        if symbol != "XAUUSD" or timeframe != "M5":
            raise ValueError("mock dataset supports only XAUUSD M5")
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        out: list[Candle] = []
        price = 2300.0
        for i in range(360):
            drift = math.sin(i / 8) * 2.0 + math.cos(i / 17) * 1.2
            open_p = price
            close = open_p + drift
            high = max(open_p, close) + abs(math.sin(i / 3)) * 0.9 + 0.15
            low = min(open_p, close) - abs(math.cos(i / 4)) * 0.9 - 0.15
            vol = 100 + (i % 20) * 4
            candle = Candle(timestamp=start + timedelta(minutes=5 * i), open=open_p, high=high, low=low, close=close, volume=vol)
            out.append(candle)
            price = close
        return out


class CsvDatasetProvider:
    base_dir = Path(__file__).resolve().parents[2] / "data" / "backtests"

    def load(self, dataset: str, symbol: str, timeframe: str) -> list[Candle]:
        filename = dataset.replace("csv:", "", 1)
        if "/" in filename or ".." in filename:
            raise ValueError("Invalid CSV filename")
        file_path = (self.base_dir / filename).resolve()
        if self.base_dir.resolve() not in file_path.parents:
            raise ValueError("Path traversal is not allowed")
        if not file_path.exists():
            raise ValueError(f"CSV dataset not found: {filename}")
        candles: list[Candle] = []
        with file_path.open("r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            required = {"timestamp", "open", "high", "low", "close", "volume"}
            if not required.issubset(set(reader.fieldnames or [])):
                raise ValueError("CSV missing required columns")
            for row in reader:
                candles.append(
                    Candle(
                        timestamp=datetime.fromisoformat(str(row["timestamp"])),
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=float(row.get("volume") or 0),
                    )
                )
        return candles
