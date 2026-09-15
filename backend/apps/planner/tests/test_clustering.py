from datetime import date
from decimal import Decimal

import pytest
from django.contrib.gis.geos import Point

from apps.catalog.tests.factories import ClimateNormalFactory, CrowdIndexFactory, SpotFactory
from apps.planner.engine.candidates import AIRPORTS
from apps.planner.engine.clustering import build_loops

pytestmark = pytest.mark.django_db

JAC_LAT, JAC_LON = AIRPORTS["JAC"]


def _spot(offset_lon, offset_lat, min_days=1):
    spot = SpotFactory(
        geom=Point(JAC_LON + offset_lon, JAC_LAT + offset_lat), min_days=min_days
    )
    ClimateNormalFactory(spot=spot, month=7, high_f="75.0", low_f="55.0", precip_in="0.0")
    CrowdIndexFactory(spot=spot, month=7, score=10)
    return spot


def test_empty_candidates_returns_no_loops():
    assert build_loops([], "JAC", 3, Decimal("4"), date(2026, 7, 1)) == []


def test_single_candidate_produces_one_loop_using_all_days():
    spot = _spot(0.1, 0.1)

    loops = build_loops([spot], "JAC", 3, Decimal("4"), date(2026, 7, 1))

    assert len(loops) == 1
    assert loops[0].days == 3
    assert sum(s.nights for s in loops[0].stops) == 3
    assert loops[0].stops[0].slug == spot.slug


def test_each_leg_respects_max_drive_hours_per_day():
    near = _spot(0.1, 0.1)
    far = _spot(20, 0)  # ~1000+ mi away, well past a 4h*50mph=200mi leg budget

    loops = build_loops([near, far], "JAC", 3, Decimal("4"), date(2026, 7, 1))

    # The far spot can never be reached from the near spot within one leg's budget,
    # so no loop should include both.
    for loop in loops:
        slugs = {s.slug for s in loop.stops}
        assert not ({near.slug, far.slug} <= slugs)


def test_more_stops_than_trip_days_is_infeasible_and_skipped():
    spots = [_spot(0.1 * i, 0.1 * i) for i in range(5)]

    # 5 spots can't each get >=1 night in a 3-day trip starting from spot index 0.
    loops = build_loops(spots[:5], "JAC", 3, Decimal("10"), date(2026, 7, 1))

    for loop in loops:
        assert len(loop.stops) <= 3


def test_varies_starting_candidate_across_loops():
    spots = [_spot(0.1 * i, 0.1 * i) for i in range(4)]

    loops = build_loops(spots, "JAC", 3, Decimal("4"), date(2026, 7, 1), max_loops=4)

    starting_slugs = {loop.stops[0].slug for loop in loops}
    assert len(starting_slugs) > 1  # more than one distinct starting point was tried


def test_loop_month_score_is_average_of_its_stops():
    spot = _spot(0.1, 0.1)

    loops = build_loops([spot], "JAC", 2, Decimal("4"), date(2026, 7, 1))

    from apps.catalog.scoring import month_score

    assert loops[0].month_score == month_score(spot, 7)
