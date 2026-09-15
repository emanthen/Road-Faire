"""candidates -> clustering -> budget, end to end (BUILD_PROMPT §4 STEPs 1-5 together
for the first time, even though the spot data is factories rather than live NPS/RIDB
data — that part is still gated on the NPS/RIDB keys, not on this pipeline)."""

from datetime import date
from decimal import Decimal

import pytest
from django.contrib.gis.geos import Point

from apps.catalog.tests.factories import ClimateNormalFactory, CrowdIndexFactory, SpotFactory
from apps.planner.engine.budget import build_trip_options
from apps.planner.engine.candidates import AIRPORTS, candidate_spots
from apps.planner.engine.clustering import build_loops
from apps.planner.engine.types import TripRequest

pytestmark = pytest.mark.django_db

JAC_LAT, JAC_LON = AIRPORTS["JAC"]


def test_full_pipeline_produces_three_ranked_tier_options():
    for i in range(3):
        spot = SpotFactory(
            geom=Point(JAC_LON + 0.1 * i, JAC_LAT + 0.1 * i), min_days=1
        )
        ClimateNormalFactory(spot=spot, month=7, high_f="75.0", low_f="55.0", precip_in="0.0")
        CrowdIndexFactory(spot=spot, month=7, score=10)

    request = TripRequest(
        origin_airport="JAC",
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 4),
        adults=2,
        children=0,
        budget_usd=Decimal("5000"),
        is_us_resident=True,
        vehicle_pref="car",
        vibe_tags=[],
        max_drive_hours_per_day=Decimal("4"),
    )

    candidates = candidate_spots(
        request.origin_airport, request.start_date, request.max_drive_hours_per_day, request.days
    )
    assert len(candidates) == 3

    loops = build_loops(
        candidates,
        request.origin_airport,
        request.days,
        request.max_drive_hours_per_day,
        request.start_date,
    )
    assert len(loops) > 0

    options = build_trip_options(loops, request)

    assert [o.tier for o in options] == ["LEAN", "BALANCED", "COMFORT"]
    for option in options:
        assert option.cost.total > 0
