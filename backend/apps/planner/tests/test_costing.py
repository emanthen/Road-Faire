from datetime import date
from decimal import Decimal

from apps.planner.engine.costing import (
    CAR_DAILY_RATE,
    CAR_MPG,
    FOOD_RATE_SELF_COOK,
    FUEL_PRICE_USD_PER_GALLON,
    MOTEL_NIGHTLY_RATE,
    cost_loop,
)
from apps.planner.engine.tiers import BALANCED, LEAN
from apps.planner.engine.types import Loop, LoopStop, TripRequest


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
