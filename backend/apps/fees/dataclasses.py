"""EntryFeeLine, EntryFeeBreakdown, PassRecommendation."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal


@dataclass(frozen=True)
class FeeRates:
    """Every dollar amount and the surcharge park list, as effective on some date —
    apps.fees.repository.load_fee_schedule() is what resolves this from FeeSchedule;
    entry_fees() takes it as a plain argument and never touches the ORM itself."""

    nonresident_surcharge: Decimal
    atb_resident: Decimal
    atb_nonresident: Decimal
    surcharge_park_slugs: frozenset[str]


@dataclass(frozen=True)
class ParkFeeInput:
    """One park in a trip, as the engine needs to know it. `standard_fee` is the park's
    normal entrance fee (from apps.catalog.SpotCost in the real flow); `fee_type` says
    whether it's charged once per vehicle or per adult."""

    slug: str
    name: str
    standard_fee: Decimal
    fee_type: Literal["vehicle", "person"] = "vehicle"


@dataclass(frozen=True)
class EntryFeeLine:
    park_name: str
    standard_fee: Decimal
    surcharge: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.standard_fee + self.surcharge


@dataclass(frozen=True)
class PassRecommendation:
    cheaper: Literal["pay_as_you_go", "annual_pass", "tie"]
    savings: Decimal
    explanation: str


@dataclass(frozen=True)
class EntryFeeBreakdown:
    lines: list[EntryFeeLine]
    pay_as_you_go_total: Decimal
    annual_pass_total: Decimal
    recommendation: PassRecommendation
