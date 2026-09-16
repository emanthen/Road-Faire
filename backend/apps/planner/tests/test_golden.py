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


# Hand-computed against the bootstrap _DEFAULT_VAN_SPEC (costing.py) and the same
# GOLDEN_LOOP (3 nights total, 240 miles) — COMFORT tier is van/motel/restaurant:
#   van base: 120/night * 3 nights = 360
#   mileage overage: included 100mi/night * 3 = 300mi >= 240mi planned -> 0
#   prep fee: 75 flat; insurance: 25/night * 3 = 75; one_way/generator/hookup/addons: 0
#     (GOLDEN_LOOP is a round trip, no drop fee — see cost_loop's one_way=False)
#   van total (== transport): 360 + 0 + 75 + 75 = 510
#   lodging (motel, 3 nights): 110 * 3 = 330
#   entry: same 470 as LEAN (residency/parks unchanged by tier)
#   fuel (van, 18mpg): 240/18 * 3.80 = 50.67 (rounded)
#   food (restaurant, 3 people, 3 days): 130 * 3 * 3 = 1170
#   subtotal: 510 + 330 + 470 + 50.67 + 1170 = 2530.67
#   buffer: 2530.67 * 0.15 = 379.60 (rounded); total: 2910.27
EXPECTED_COMFORT_TOTAL = Decimal("2910.27")
EXPECTED_VAN_BASE = Decimal("360")
EXPECTED_VAN_INSURANCE = Decimal("75")
EXPECTED_VAN_PREP_FEE = Decimal("75")


def test_golden_request_produces_an_itemised_van_breakdown_not_a_collapsed_number():
    options = build_trip_options([GOLDEN_LOOP], GOLDEN_REQUEST)

    comfort = next(o for o in options if o.tier == "COMFORT")
    assert comfort.cost.total == EXPECTED_COMFORT_TOTAL

    van = comfort.cost.van_breakdown
    assert van is not None
    assert van.base == EXPECTED_VAN_BASE
    assert van.mileage_overage == Decimal("0")
    assert van.prep_fee == EXPECTED_VAN_PREP_FEE
    assert van.insurance == EXPECTED_VAN_INSURANCE
    assert van.one_way_fee == Decimal("0")
    assert van.total == comfort.cost.transport

    # Non-van tiers carry no itemised breakdown — nothing to collapse.
    lean = next(o for o in options if o.tier == "LEAN")
    assert lean.cost.van_breakdown is None


def test_golden_request_surfaces_the_pass_recommendation_on_every_tier():
    options = build_trip_options([GOLDEN_LOOP], GOLDEN_REQUEST)

    for option in options:
        # 2 non-resident adults, 2 surcharge parks -> pay-as-you-go entry ($470 across
        # all tiers) beats one $250 non-resident pass ($500) here, same trade-off
        # apps.fees.engine already proves — the point is the planner surfaces it, not
        # decides it.
        assert option.cost.entry_annual_pass_total == Decimal("500")
        assert option.cost.entry_recommendation.cheaper == "pay_as_you_go"
        assert option.cost.entry_recommendation.explanation
