"""Frozen dataclasses for all engine I/O (TripRequest, Loop, CostBreakdown, ...)."""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Literal

from apps.fees.dataclasses import PassRecommendation
from apps.vehicles.pricing import VanCostBreakdown


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
    # State abbreviation (e.g. "WY") — which RateCard region this stop's lodging/car
    # rates should look up. Empty when unknown (hand-built test loops).
    region: str = ""


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
    entry: Decimal  # pay-as-you-go total — the conservative default folded into subtotal/total
    fuel: Decimal
    food: Decimal
    activities: Decimal
    subtotal: Decimal
    buffer: Decimal
    total: Decimal
    entry_annual_pass_total: Decimal
    entry_recommendation: PassRecommendation
    van_breakdown: VanCostBreakdown | None = None
    # Which of {"lodging", "transport", "fuel"} came from a bootstrap assumption rather
    # than a real, cited RateCard/EIA figure — "$95-140/night (estimate)" is honest,
    # "$120.00" from the same guess is a lie with a decimal point (BUILD_PROMPT C2).
    estimated_categories: frozenset[str] = frozenset()
    lodging_range: tuple[Decimal, Decimal] | None = None
    transport_range: tuple[Decimal, Decimal] | None = None


@dataclass(frozen=True)
class TripOption:
    tier: Literal["LEAN", "BALANCED", "COMFORT"]
    loop: Loop
    cost: CostBreakdown
    # Populated by the view after cost_all_tiers() returns — narrative generation makes
    # an external API call, so it happens outside the pure engine, same reason rates/
    # van_spec/fuel_price are resolved there instead of inside cost_loop().
    narrative: str = ""
