"""generate_plan_async — status transitions pending -> running -> done/failed."""

from datetime import date
from decimal import Decimal

import pytest
from django.contrib.gis.geos import Point

from apps.catalog.tests.factories import ClimateNormalFactory, CrowdIndexFactory, SpotFactory
from apps.planner.engine.candidates import AIRPORTS
from apps.planner.models import TripRequest
from apps.planner.tasks import generate_plan_async

pytestmark = pytest.mark.django_db

JAC_LAT, JAC_LON = AIRPORTS["JAC"]


def _seed_spots(n=2):
    for i in range(n):
        spot = SpotFactory(geom=Point(JAC_LON + 0.1 * i, JAC_LAT + 0.1 * i), min_days=1)
        ClimateNormalFactory(spot=spot, month=7, high_f="75.0", low_f="55.0", precip_in="0.0")
        CrowdIndexFactory(spot=spot, month=7, score=10)


def _pending_trip_request(**overrides) -> TripRequest:
    defaults = dict(
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
        status=TripRequest.Status.PENDING,
    )
    defaults.update(overrides)
    return TripRequest.objects.create(**defaults)


def test_successful_generation_ends_done_with_itineraries():
    _seed_spots(2)
    db_request = _pending_trip_request()

    generate_plan_async(db_request.id)

    db_request.refresh_from_db()
    assert db_request.status == TripRequest.Status.DONE
    assert db_request.itineraries.count() == 3  # LEAN, BALANCED, COMFORT


def test_nothing_fits_budget_ends_failed_not_done():
    _seed_spots(2)
    db_request = _pending_trip_request(budget_usd=Decimal("1.00"))

    generate_plan_async(db_request.id)

    db_request.refresh_from_db()
    assert db_request.status == TripRequest.Status.FAILED
    assert db_request.itineraries.count() == 0


def test_unknown_airport_ends_failed_not_raised():
    db_request = _pending_trip_request(origin_airport="ZZZ")

    generate_plan_async(db_request.id)  # must not raise — Celery would just retry/drop it

    db_request.refresh_from_db()
    assert db_request.status == TripRequest.Status.FAILED
