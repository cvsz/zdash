from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class InstrumentMetadata(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    asset_class: str = Field(default="commodity", min_length=1, max_length=32)
    sector: str | None = Field(default=None, max_length=64)
    tick_size: float | None = Field(default=None, gt=0)
    lower_price_band: float | None = Field(default=None, gt=0)
    upper_price_band: float | None = Field(default=None, gt=0)
    contract_multiplier: float | None = Field(default=None, gt=0)
    source: str = Field(default="operator", min_length=1, max_length=64)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.strip().upper()


class InstrumentRegistry:
    """Trusted reference-data registry loaded from operator-supplied JSON.

    Unknown instruments fail open on band/tick checks (returns known=False) so the
    caller can decide; use ``require`` flows for fail-closed validation.
    """

    def __init__(self, metadata_json: str = "") -> None:
        self._items: dict[str, InstrumentMetadata] = {}
        if metadata_json.strip():
            self.load_json(metadata_json)

    def load_json(self, payload: str) -> None:
        raw = json.loads(payload)
        rows = raw if isinstance(raw, list) else raw.get("instruments", [])
        if not isinstance(rows, list):
            raise ValueError("instrument metadata must be a list")
        for row in rows:
            self.upsert(InstrumentMetadata.model_validate(row))

    def upsert(self, metadata: InstrumentMetadata) -> InstrumentMetadata:
        self._items[metadata.symbol] = metadata
        return metadata

    def get(self, symbol: str) -> InstrumentMetadata | None:
        return self._items.get(symbol.upper())

    def list(self) -> list[InstrumentMetadata]:
        return sorted(self._items.values(), key=lambda item: item.symbol)

    def validate_price(
        self,
        symbol: str,
        price: float | None,
    ) -> tuple[bool, bool, bool]:
        """Returns (known, price_band_ok, tick_size_ok)."""
        metadata = self.get(symbol)
        if metadata is None or price is None:
            return metadata is not None, True, True
        band_ok = True
        if metadata.lower_price_band is not None and price < metadata.lower_price_band:
            band_ok = False
        if metadata.upper_price_band is not None and price > metadata.upper_price_band:
            band_ok = False
        tick_ok = True
        if metadata.tick_size:
            units = price / metadata.tick_size
            tick_ok = abs(units - round(units)) <= 1e-7
        return True, band_ok, tick_ok


PriceBandDecision = Literal[
    "accepted", "unknown_instrument", "band_violation", "tick_violation"
]


def validate_order_price(
    registry: InstrumentRegistry,
    symbol: str,
    price: float | None,
) -> PriceBandDecision:
    """Fail-closed single verdict for pre-trade price sanity."""
    known, band_ok, tick_ok = registry.validate_price(symbol, price)
    if not known:
        return "unknown_instrument"
    if not band_ok:
        return "band_violation"
    if not tick_ok:
        return "tick_violation"
    return "accepted"


DEFAULT_INSTRUMENTS: list[InstrumentMetadata] = [
    InstrumentMetadata(
        symbol="XAUUSD",
        asset_class="commodity",
        sector="metals",
        tick_size=0.01,
        contract_multiplier=100.0,
        source="default",
    ),
]
