"""transport + lodging + entry + fuel + food + activities (BUILD_PROMPT §4 STEP 3).

Per-day/per-night rates below are cost-model assumptions this planner uses to estimate
a trip, not cited real-world facts — unlike apps.fees.constants, they don't carry a
SOURCE_URL. They're deliberately named constants (not magic numbers inline) so the
planner UI can expose/adjust them later.
"""

from decimal import Decimal

from apps.fees.dataclasses import ParkFeeInput
from apps.fees.engine import entry_fees
from apps.planner.engine.tiers import TierPreset
from apps.planner.engine.types import CostBreakdown, Loop, TripRequest

# --- transport: per-day rate by vehicle type ---
CAR_DAILY_RATE = Decimal("65")
VAN_DAILY_RATE = Decimal("120")

# --- lodging: per-night rate by lodging type ---
CAMPSITE_NIGHTLY_RATE = Decimal("30")
MOTEL_NIGHTLY_RATE = Decimal("110")
MIXED_NIGHTLY_RATE = (CAMPSITE_NIGHTLY_RATE + MOTEL_NIGHTLY_RATE) / 2

# --- fuel ---
CAR_MPG = Decimal("30")
VAN_MPG = Decimal("18")
FUEL_PRICE_USD_PER_GALLON = Decimal("3.80")

# --- food: exact rates from BUILD_PROMPT §4 ---
FOOD_RATE_SELF_COOK = Decimal("35")
FOOD_RATE_MIXED = Decimal("75")
FOOD_RATE_RESTAURANT = Decimal("130")

BUFFER_RATE = Decimal("0.15")

_LODGING_RATES = {
    "campsite": CAMPSITE_NIGHTLY_RATE,
    "motel": MOTEL_NIGHTLY_RATE,
    "mixed": MIXED_NIGHTLY_RATE,
}
_FOOD_RATES = {
    "self_cook": FOOD_RATE_SELF_COOK,
    "mixed": FOOD_RATE_MIXED,
    "restaurant": FOOD_RATE_RESTAURANT,
}


def cost_loop(loop: Loop, request: TripRequest, tier: TierPreset) -> CostBreakdown:
    transport = (VAN_DAILY_RATE if tier.vehicle == "van" else CAR_DAILY_RATE) * loop.days

    nights = sum(stop.nights for stop in loop.stops)
    lodging = _LODGING_RATES[tier.lodging] * nights

    entry_inputs = [
        ParkFeeInput(
            slug=stop.slug, name=stop.name, standard_fee=stop.standard_fee, fee_type=stop.fee_type
        )
        for stop in loop.stops
    ]
    entry_breakdown = entry_fees(
        entry_inputs,
        adults_16plus=request.adults,
        is_us_resident=request.is_us_resident,
        children_under_16=request.children,
    )
    # Pay-as-you-go is the conservative default for a single trip's cost estimate — the
    # pass-vs-pay-as-you-go recommendation itself is surfaced to the user separately
    # (apps.fees), not decided silently inside the planner's cost total.
    entry = entry_breakdown.pay_as_you_go_total

    mpg = VAN_MPG if tier.vehicle == "van" else CAR_MPG
    fuel = (loop.total_miles / mpg) * FUEL_PRICE_USD_PER_GALLON

    food = _FOOD_RATES[tier.food_tier] * request.people * loop.days

    # No price data modeled on apps.catalog.Activity yet (no cost field on that model) —
    # not guessed at here.
    activities = Decimal("0")

    subtotal = transport + lodging + entry + fuel + food + activities
    buffer = subtotal * BUFFER_RATE
    total = subtotal + buffer

    return CostBreakdown(
        transport=transport,
        lodging=lodging,
        entry=entry,
        fuel=fuel,
        food=food,
        activities=activities,
        subtotal=subtotal,
        buffer=buffer,
        total=total,
    )
