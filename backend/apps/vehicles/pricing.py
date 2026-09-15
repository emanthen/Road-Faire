"""true_cost(spec, nights, miles, one_way) — itemised (BUILD_PROMPT §4.1).

Never a single teaser number: every call site gets the full itemised VanCostBreakdown,
there's no collapsed/summary-only path.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class VehicleSpecInput:
    """Decoupled from the ORM, same pattern as apps.fees.dataclasses.ParkFeeInput."""

    length_ft: Decimal
    height_ft: Decimal
    included_miles_per_night: int
    overage_rate_per_mile: Decimal
    base_nightly_rate: Decimal
    prep_fee: Decimal
    insurance_per_night: Decimal
    one_way_fee: Decimal
    generator_rate_per_hour: Decimal
    hookup_premium_per_night: Decimal


@dataclass(frozen=True)
class Addon:
    name: str
    cost: Decimal


@dataclass(frozen=True)
class VanCostBreakdown:
    base: Decimal
    mileage_overage: Decimal
    prep_fee: Decimal
    insurance: Decimal
    one_way_fee: Decimal
    generator: Decimal
    hookup_premium: Decimal
    addons: Decimal
    total: Decimal


def true_cost(
    spec: VehicleSpecInput,
    nights: int,
    planned_miles: Decimal,
    one_way: bool,
    generator_hours: Decimal = Decimal("0"),
    hookup_nights: int = 0,
    addons: list[Addon] | None = None,
) -> VanCostBreakdown:
    base = spec.base_nightly_rate * nights

    included_miles = spec.included_miles_per_night * nights
    overage_miles = max(Decimal("0"), planned_miles - included_miles)
    mileage_overage = overage_miles * spec.overage_rate_per_mile

    prep_fee = spec.prep_fee  # one-time, not multiplied by nights

    insurance = spec.insurance_per_night * nights

    one_way_fee = spec.one_way_fee if one_way else Decimal("0")

    generator = spec.generator_rate_per_hour * generator_hours

    hookup_premium = spec.hookup_premium_per_night * hookup_nights

    addons_total = sum((a.cost for a in addons or []), Decimal("0"))

    total = (
        base
        + mileage_overage
        + prep_fee
        + insurance
        + one_way_fee
        + generator
        + hookup_premium
        + addons_total
    )

    return VanCostBreakdown(
        base=base,
        mileage_overage=mileage_overage,
        prep_fee=prep_fee,
        insurance=insurance,
        one_way_fee=one_way_fee,
        generator=generator,
        hookup_premium=hookup_premium,
        addons=addons_total,
        total=total,
    )
