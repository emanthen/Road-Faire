"""Frozen dataclasses for all engine I/O (TripRequest, Loop, CostBreakdown, ...)."""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Literal


@dataclass(frozen=True)
class TripRequest:
    origin_airport: str
    start_date: date
    end_date: date
    adults: int
    children: int
    budget_usd: Decimal
    is_us_resident: bool
    vehicle_pref: Literal["van", "car"]
    vibe_tags: list[str]
    max_drive_hours_per_day: Decimal

    @property
    def days(self) -> int:
        return (self.end_date - self.start_date).days

    @property
    def people(self) -> int:
        return self.adults + self.children


@dataclass(frozen=True)
class LoopStopActivity:
    """A trail or tour available at a stop — what there is to actually do there."""

    name: str
    kind: Literal["trail", "tour"]


@dataclass(frozen=True)
class LoopStop:
    """One spot in a candidate route."""

    slug: str
    name: str
    standard_fee: Decimal
    fee_type: Literal["vehicle", "person"]
    nights: int
    latitude: float = 0.0
    longitude: float = 0.0
    activities: list[LoopStopActivity] = field(default_factory=list)


@dataclass(frozen=True)
class Loop:
    """A candidate route. What clustering.py will eventually produce; hand-built in
    tests until candidates.py/clustering.py exist (need live Spot/DriveTime data)."""

    stops: list[LoopStop]
    total_miles: Decimal
    days: int
    month_score: int


@dataclass(frozen=True)
class CostBreakdown:
    transport: Decimal
    lodging: Decimal
    entry: Decimal
    fuel: Decimal
    food: Decimal
    activities: Decimal
    subtotal: Decimal
    buffer: Decimal
    total: Decimal


@dataclass(frozen=True)
class TripOption:
    tier: Literal["LEAN", "BALANCED", "COMFORT"]
    loop: Loop
    cost: CostBreakdown
