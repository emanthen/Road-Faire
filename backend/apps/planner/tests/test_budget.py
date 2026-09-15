from datetime import date
from decimal import Decimal

from apps.planner.engine.budget import build_trip_options, rank_loops
from apps.planner.engine.types import Loop, TripRequest


def _request(budget_usd: Decimal) -> TripRequest:
    return TripRequest(
        origin_airport="JAC",
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 3),
        adults=2,
        children=0,
        budget_usd=budget_usd,
        is_us_resident=True,
        vehicle_pref="car",
        vibe_tags=[],
        max_drive_hours_per_day=Decimal("4"),
    )


def test_filters_out_loops_over_budget():
    # LEAN total for a 2-day/2-person loop is ~$318 at 50 miles (fixed transport+food
    # dominate) and ~$602 at 2000 miles (fuel now matters) — $400 sits between them.
    cheap = Loop(stops=[], total_miles=Decimal("50"), days=2, month_score=80)
    expensive = Loop(stops=[], total_miles=Decimal("2000"), days=2, month_score=90)

    ranked = rank_loops([cheap, expensive], _request(budget_usd=Decimal("400")))

    assert cheap in ranked
    assert expensive not in ranked


def test_ties_break_on_month_score_descending():
    low_score = Loop(stops=[], total_miles=Decimal("50"), days=2, month_score=40)
    high_score = Loop(stops=[], total_miles=Decimal("50"), days=2, month_score=90)

    ranked = rank_loops([low_score, high_score], _request(budget_usd=Decimal("2000")))

    assert ranked == [high_score, low_score]


def test_build_trip_options_returns_three_tiers_for_best_loop():
    loop = Loop(stops=[], total_miles=Decimal("50"), days=2, month_score=80)

    options = build_trip_options([loop], _request(budget_usd=Decimal("2000")))

    assert [o.tier for o in options] == ["LEAN", "BALANCED", "COMFORT"]
    assert all(o.loop == loop for o in options)


def test_build_trip_options_returns_empty_when_nothing_affordable():
    loop = Loop(stops=[], total_miles=Decimal("5000"), days=2, month_score=80)

    options = build_trip_options([loop], _request(budget_usd=Decimal("10")))

    assert options == []
