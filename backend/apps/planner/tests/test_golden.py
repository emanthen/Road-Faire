"""Fixed request -> fixed dollar total, byte-comparable (Phase 5 gate).

Scoped to what's buildable this phase: costing -> tiers -> budget against a hand-built
Loop, bypassing candidates.py/clustering.py (blocked on live Spot/DriveTime data). Not
the full "request in, three costed itineraries out" pipeline BUILD_PROMPT describes —
that needs candidates/clustering, which don't exist yet. This is the honest, narrower
version: the math from a known loop is exactly reproducible.
"""

from datetime import date
from decimal import Decimal

from apps.planner.engine.budget import build_trip_options
from apps.planner.engine.types import Loop, LoopStop, TripRequest

GOLDEN_REQUEST = TripRequest(
    origin_airport="JAC",
    start_date=date(2026, 7, 1),
    end_date=date(2026, 7, 4),
    adults=2,
    children=1,
    budget_usd=Decimal("2500"),
    is_us_resident=False,
    vehicle_pref="car",
    vibe_tags=["mountains"],
    max_drive_hours_per_day=Decimal("4"),
)

GOLDEN_LOOP = Loop(
    stops=[
        LoopStop(
            slug="yell", name="Yellowstone", standard_fee=Decimal("35"), fee_type="vehicle",
            nights=2,
        ),
        LoopStop(
            slug="grte", name="Grand Teton", standard_fee=Decimal("35"), fee_type="vehicle",
            nights=1,
        ),
    ],
    total_miles=Decimal("240"),
    days=3,
    month_score=85,
)

# Hand-computed, not derived from the code under test:
#   entry: (35+35) standard + (100 * 2 adults * 2 surcharge parks) surcharge = 470
#   fuel (LEAN/car, 30mpg): 240/30 * 3.80 = 30.40
#   food (LEAN/self_cook): 35 * 3 people * 3 days = 315
#   lodging (LEAN/campsite, 3 nights total): 30 * 3 = 90
#   transport (LEAN/car): 65 * 3 days = 195
#   subtotal: 195 + 90 + 470 + 30.40 + 315 = 1100.40
#   buffer: 1100.40 * 0.15 = 165.06
#   total: 1265.46
EXPECTED_LEAN_TOTAL = Decimal("1265.46")


def test_golden_request_produces_golden_total():
    options = build_trip_options([GOLDEN_LOOP], GOLDEN_REQUEST)

    lean = next(o for o in options if o.tier == "LEAN")
    assert lean.cost.total == EXPECTED_LEAN_TOTAL
