"""rank, filter to budget, 15% buffer (BUILD_PROMPT §4 STEP 4-5)."""

from apps.fees.dataclasses import FeeRates
from apps.planner.engine.tiers import LEAN, cost_all_tiers
from apps.planner.engine.types import Loop, TripOption, TripRequest


def rank_loops(
    loops: list[Loop], request: TripRequest, rates: FeeRates | None = None
) -> list[Loop]:
    """Filters to loops whose cheapest tier (LEAN) fits the budget, tie-breaks on
    month_score descending."""
    from apps.planner.engine.costing import cost_loop

    affordable = [
        loop
        for loop in loops
        if cost_loop(loop, request, LEAN, rates).total <= request.budget_usd
    ]
    return sorted(affordable, key=lambda loop: loop.month_score, reverse=True)


def build_trip_options(
    loops: list[Loop], request: TripRequest, rates: FeeRates | None = None
) -> list[TripOption]:
    """Ranks candidate loops, returns the best-fitting one's 3 tier variants."""
    ranked = rank_loops(loops, request, rates)
    if not ranked:
        return []
    return cost_all_tiers(ranked[0], request, rates)
