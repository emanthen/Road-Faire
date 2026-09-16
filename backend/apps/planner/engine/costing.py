"""transport + lodging + entry + fuel + food + activities (BUILD_PROMPT §4 STEP 3).

Per-day/per-night rates below are cost-model assumptions this planner uses to estimate
a trip, not cited real-world facts — unlike apps.fees.constants, they don't carry a
SOURCE_URL. They're deliberately named constants (not magic numbers inline) so the
planner UI can expose/adjust them later.
"""

from decimal import Decimal

from apps.core.money import usd
from apps.fees.dataclasses import FeeRates, ParkFeeInput
from apps.fees.engine import entry_fees
from apps.planner.engine.tiers import TierPreset
from apps.planner.engine.types import CostBreakdown, Loop, TripRequest
from apps.planner.rates import FALLBACK_BANDS, RateRange
from apps.vehicles.pricing import VehicleSpecInput, true_cost

# Bootstrap van spec, same status as the old flat VAN_DAILY_RATE constant — a
# cost-model assumption, not a cited real quote. Used only when no VehicleSpec row
# exists in the DB yet (Block D3 hasn't seeded real rental classes); the view passes a
# real VehicleSpecInput once one does. Every line item through this spec is exactly as
# "estimate" as VAN_DAILY_RATE used to be — true_cost() just itemises the same guess
# instead of collapsing it.
_DEFAULT_VAN_SPEC = VehicleSpecInput(
    length_ft=Decimal("22"),
    height_ft=Decimal("10"),
    included_miles_per_night=100,
    overage_rate_per_mile=Decimal("0.45"),
    base_nightly_rate=Decimal("120"),
    prep_fee=Decimal("75"),
    insurance_per_night=Decimal("25"),
    one_way_fee=Decimal("350"),
    generator_rate_per_hour=Decimal("3"),
    hookup_premium_per_night=Decimal("15"),
)

# --- fuel ---
CAR_MPG = Decimal("30")
VAN_MPG = Decimal("18")
# Bootstrap fallback — apps.planner.fuel.BOOTSTRAP_FUEL_PRICE is the source of truth;
# duplicated here only so tests that don't care about fuel can import a stable name.
FUEL_PRICE_USD_PER_GALLON = Decimal("3.80")

# --- food: exact rates from BUILD_PROMPT §4 ---
FOOD_RATE_SELF_COOK = Decimal("35")
FOOD_RATE_MIXED = Decimal("75")
FOOD_RATE_RESTAURANT = Decimal("130")

BUFFER_RATE = Decimal("0.15")

_FOOD_RATES = {
    "self_cook": FOOD_RATE_SELF_COOK,
    "mixed": FOOD_RATE_MIXED,
    "restaurant": FOOD_RATE_RESTAURANT,
}


def _lodging_range(lodging_type: str, rate_ranges: dict[str, RateRange]) -> RateRange:
    if lodging_type == "mixed":
        campsite, motel = rate_ranges["campsite"], rate_ranges["motel"]
        return RateRange(
            low=(campsite.low + motel.low) / 2,
            high=(campsite.high + motel.high) / 2,
            is_estimate=campsite.is_estimate or motel.is_estimate,
        )
    return rate_ranges[lodging_type]


def cost_loop(
    loop: Loop,
    request: TripRequest,
    tier: TierPreset,
    rates: FeeRates | None = None,
    van_spec: VehicleSpecInput | None = None,
    rate_ranges: dict[str, RateRange] | None = None,
    fuel_price: tuple[Decimal, bool] | None = None,
) -> CostBreakdown:
    """Pure — no ORM, no cache access. `rates`, `van_spec`, `rate_ranges` and
    `fuel_price` are all passed down from the view (apps.planner.views.create_plan
    loads them once and threads them through build_trip_options -> cost_all_tiers ->
    here); omitting any falls back to a bootstrap default, same pattern as
    apps.fees.engine.entry_fees(). `fuel_price` is (price_per_gallon, is_estimate) from
    apps.planner.fuel.current_fuel_price_per_gallon()."""

    rate_ranges = rate_ranges if rate_ranges is not None else FALLBACK_BANDS
    estimated: set[str] = set()

    nights = sum(stop.nights for stop in loop.stops)

    van_breakdown = None
    transport_range = None
    if tier.vehicle == "van":
        spec = van_spec if van_spec is not None else _DEFAULT_VAN_SPEC
        if van_spec is None:
            estimated.add("transport")
        van_breakdown = true_cost(
            spec,
            nights=nights,
            planned_miles=loop.total_miles,
            # Loops are round trips back to the origin airport — candidates.py /
            # clustering.py don't model a separate drop-off location yet, so a one-way
            # fee never applies to a planner-generated itinerary today.
            one_way=False,
        )
        transport = van_breakdown.total
    else:
        car_range = rate_ranges["car"]
        transport_range = (car_range.low * loop.days, car_range.high * loop.days)
        if car_range.is_estimate:
            estimated.add("transport")
        transport = usd(car_range.midpoint * loop.days)

    lodging_range_rate = _lodging_range(tier.lodging, rate_ranges)
    lodging_range = (lodging_range_rate.low * nights, lodging_range_rate.high * nights)
    if lodging_range_rate.is_estimate:
        estimated.add("lodging")
    lodging = usd(lodging_range_rate.midpoint * nights)

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
        rates=rates,
        children_under_16=request.children,
    )
    # Pay-as-you-go is the conservative default folded into subtotal/total — the annual
    # pass total and recommendation are still carried on CostBreakdown (not decided
    # silently here) so the itinerary can surface "buy the pass and save $X".
    entry = entry_breakdown.pay_as_you_go_total

    mpg = VAN_MPG if tier.vehicle == "van" else CAR_MPG
    price_per_gallon, fuel_is_estimate = (
        fuel_price if fuel_price is not None else (FUEL_PRICE_USD_PER_GALLON, True)
    )
    fuel = usd((loop.total_miles / mpg) * price_per_gallon)
    if fuel_is_estimate:
        estimated.add("fuel")

    food = usd(_FOOD_RATES[tier.food_tier] * request.people * loop.days)

    # No price data modeled on apps.catalog.Activity yet (no cost field on that model) —
    # not guessed at here.
    activities = Decimal("0")

    subtotal = transport + lodging + entry + fuel + food + activities
    buffer = usd(subtotal * BUFFER_RATE)
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
        entry_annual_pass_total=entry_breakdown.annual_pass_total,
        entry_recommendation=entry_breakdown.recommendation,
        van_breakdown=van_breakdown,
        estimated_categories=frozenset(estimated),
        lodging_range=lodging_range,
        transport_range=transport_range,
    )
