from datetime import date
from decimal import Decimal

from apps.planner.engine.costing import (
    CAR_MPG,
    FOOD_RATE_SELF_COOK,
    FUEL_PRICE_USD_PER_GALLON,
    cost_loop,
)
from apps.planner.engine.tiers import BALANCED, COMFORT, LEAN
from apps.planner.engine.types import Loop, LoopStop, TripRequest
from apps.planner.rates import FALLBACK_BANDS, RateRange
from apps.vehicles.pricing import VehicleSpecInput

CAR_DAILY_RATE = FALLBACK_BANDS["car"].midpoint
MOTEL_NIGHTLY_RATE = FALLBACK_BANDS["motel"].midpoint


def _request(**overrides) -> TripRequest:
    defaults = dict(
        origin_airport="JAC",
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 4),
        adults=2,
        children=0,
        budget_usd=Decimal("2000"),
        is_us_resident=True,
        vehicle_pref="car",
        vibe_tags=[],
        max_drive_hours_per_day=Decimal("4"),
    )
    defaults.update(overrides)
    return TripRequest(**defaults)


def test_transport_scales_with_days_and_vehicle():
    loop = Loop(stops=[], total_miles=Decimal("0"), days=3, month_score=80)
    cost = cost_loop(loop, _request(), LEAN)
    assert cost.transport == CAR_DAILY_RATE * 3


def test_lodging_scales_with_total_nights_across_stops():
    loop = Loop(
        stops=[
            LoopStop(slug="a", name="A", standard_fee=Decimal("0"), fee_type="vehicle", nights=2),
            LoopStop(slug="b", name="B", standard_fee=Decimal("0"), fee_type="vehicle", nights=1),
        ],
        total_miles=Decimal("0"),
        days=3,
        month_score=80,
    )
    cost = cost_loop(loop, _request(), BALANCED)
    assert cost.lodging == MOTEL_NIGHTLY_RATE * 3


def test_fuel_uses_build_prompt_formula():
    loop = Loop(stops=[], total_miles=Decimal("300"), days=1, month_score=80)
    cost = cost_loop(loop, _request(), LEAN)
    assert cost.fuel == (Decimal("300") / CAR_MPG) * FUEL_PRICE_USD_PER_GALLON


def test_food_uses_exact_build_prompt_rate_and_scales_with_people_and_days():
    loop = Loop(stops=[], total_miles=Decimal("0"), days=4, month_score=80)
    cost = cost_loop(loop, _request(adults=2, children=1), LEAN)
    assert cost.food == FOOD_RATE_SELF_COOK * 3 * 4


def test_entry_delegates_to_fees_engine_for_surcharge_park():
    loop = Loop(
        stops=[
            LoopStop(
                slug="yell", name="Yellowstone", standard_fee=Decimal("35"), fee_type="vehicle",
                nights=1,
            )
        ],
        total_miles=Decimal("0"),
        days=1,
        month_score=80,
    )
    cost = cost_loop(loop, _request(adults=2, is_us_resident=False), LEAN)
    # 35 standard + (100 * 2 adults) surcharge = 235
    assert cost.entry == Decimal("235")


def test_subtotal_buffer_and_total_are_consistent():
    loop = Loop(stops=[], total_miles=Decimal("0"), days=2, month_score=80)
    cost = cost_loop(loop, _request(), LEAN)
    expected_subtotal = cost.transport + cost.lodging + cost.entry + cost.fuel + cost.food
    assert cost.subtotal == expected_subtotal
    assert cost.buffer == expected_subtotal * Decimal("0.15")
    assert cost.total == expected_subtotal + cost.buffer


def test_van_tier_calls_true_cost_and_itemises_transport():
    loop = Loop(
        stops=[
            LoopStop(slug="a", name="A", standard_fee=Decimal("0"), fee_type="vehicle", nights=2),
        ],
        total_miles=Decimal("500"),
        days=3,
        month_score=80,
    )
    cost = cost_loop(loop, _request(vehicle_pref="van"), COMFORT)

    assert cost.van_breakdown is not None
    assert cost.van_breakdown.total == cost.transport


def test_van_spec_argument_overrides_the_bootstrap_default():
    loop = Loop(
        stops=[
            LoopStop(slug="a", name="A", standard_fee=Decimal("0"), fee_type="vehicle", nights=1),
        ],
        total_miles=Decimal("0"),
        days=1,
        month_score=80,
    )
    spec = VehicleSpecInput(
        length_ft=Decimal("20"),
        height_ft=Decimal("9"),
        included_miles_per_night=200,
        overage_rate_per_mile=Decimal("0.30"),
        base_nightly_rate=Decimal("999"),
        prep_fee=Decimal("0"),
        insurance_per_night=Decimal("0"),
        one_way_fee=Decimal("0"),
        generator_rate_per_hour=Decimal("0"),
        hookup_premium_per_night=Decimal("0"),
    )

    cost = cost_loop(loop, _request(vehicle_pref="van"), COMFORT, van_spec=spec)

    assert cost.van_breakdown is not None
    assert cost.van_breakdown.base == Decimal("999")


def test_car_tier_has_no_van_breakdown():
    loop = Loop(stops=[], total_miles=Decimal("0"), days=1, month_score=80)
    cost = cost_loop(loop, _request(), LEAN)

    assert cost.van_breakdown is None


def test_entry_annual_pass_total_and_recommendation_are_always_populated():
    loop = Loop(stops=[], total_miles=Decimal("0"), days=1, month_score=80)
    cost = cost_loop(loop, _request(), LEAN)

    assert cost.entry_annual_pass_total is not None
    assert cost.entry_recommendation is not None
    assert cost.entry_recommendation.explanation


def test_fallback_rates_flag_lodging_transport_and_fuel_as_estimates():
    loop = Loop(stops=[], total_miles=Decimal("100"), days=1, month_score=80)
    cost = cost_loop(loop, _request(), LEAN)

    assert cost.estimated_categories == frozenset({"lodging", "transport", "fuel"})
    assert cost.lodging_range is not None
    assert cost.transport_range is not None


def test_real_fuel_price_is_not_flagged_as_an_estimate():
    loop = Loop(stops=[], total_miles=Decimal("300"), days=1, month_score=80)
    cost = cost_loop(loop, _request(), LEAN, fuel_price=(Decimal("4.10"), False))

    assert "fuel" not in cost.estimated_categories
    assert cost.fuel == (Decimal("300") / CAR_MPG * Decimal("4.10")).quantize(Decimal("0.01"))


def test_real_rate_card_row_is_not_flagged_as_an_estimate():
    loop = Loop(
        stops=[
            LoopStop(slug="a", name="A", standard_fee=Decimal("0"), fee_type="vehicle", nights=2),
        ],
        total_miles=Decimal("0"),
        days=2,
        month_score=80,
    )
    real_car = RateRange(low=Decimal("50"), high=Decimal("60"), is_estimate=False)
    rate_ranges = {**FALLBACK_BANDS, "car": real_car}

    cost = cost_loop(loop, _request(), LEAN, rate_ranges=rate_ranges)

    assert "transport" not in cost.estimated_categories
    assert "lodging" in cost.estimated_categories  # campsite still fell back
    assert cost.transport == real_car.midpoint * 2  # LEAN/car, 2 days


def test_van_tier_with_a_real_spec_is_not_flagged_as_a_transport_estimate():
    loop = Loop(
        stops=[
            LoopStop(slug="a", name="A", standard_fee=Decimal("0"), fee_type="vehicle", nights=1),
        ],
        total_miles=Decimal("0"),
        days=1,
        month_score=80,
    )
    spec = VehicleSpecInput(
        length_ft=Decimal("20"),
        height_ft=Decimal("9"),
        included_miles_per_night=200,
        overage_rate_per_mile=Decimal("0.30"),
        base_nightly_rate=Decimal("150"),
        prep_fee=Decimal("0"),
        insurance_per_night=Decimal("0"),
        one_way_fee=Decimal("0"),
        generator_rate_per_hour=Decimal("0"),
        hookup_premium_per_night=Decimal("0"),
    )

    cost = cost_loop(loop, _request(vehicle_pref="van"), COMFORT, van_spec=spec)

    assert "transport" not in cost.estimated_categories


def test_mixed_lodging_averages_campsite_and_motel_ranges():
    loop = Loop(
        stops=[
            LoopStop(slug="a", name="A", standard_fee=Decimal("0"), fee_type="vehicle", nights=1),
        ],
        total_miles=Decimal("0"),
        days=1,
        month_score=80,
    )
    campsite = FALLBACK_BANDS["campsite"]
    motel = FALLBACK_BANDS["motel"]
    expected_low, expected_high = (
        (campsite.low + motel.low) / 2,
        (campsite.high + motel.high) / 2,
    )

    cost = cost_loop(
        loop,
        _request(),
        type(BALANCED)(name="BALANCED", vehicle="car", lodging="mixed", food_tier="mixed"),
    )

    assert cost.lodging_range == (expected_low, expected_high)
