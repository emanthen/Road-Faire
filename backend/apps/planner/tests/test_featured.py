"""GET /api/plan/featured — the /trips gallery's data source."""

import pytest
from django.contrib.gis.geos import Point

from apps.catalog.tests.factories import ClimateNormalFactory, CrowdIndexFactory, SpotFactory
from apps.planner.engine.candidates import AIRPORTS
from apps.planner.models import TripRequest

pytestmark = pytest.mark.django_db

JAC_LAT, JAC_LON = AIRPORTS["JAC"]


def _seed_spots(n=2):
    for i in range(n):
        spot = SpotFactory(geom=Point(JAC_LON + 0.1 * i, JAC_LAT + 0.1 * i), min_days=1)
        ClimateNormalFactory(spot=spot, month=7, high_f="75.0", low_f="55.0", precip_in="0.0")
        CrowdIndexFactory(spot=spot, month=7, score=10)


def _payload(**overrides):
    payload = {
        "origin_airport": "JAC",
        "start_date": "2026-07-01",
        "end_date": "2026-07-04",
        "adults": 2,
        "children": 0,
        "budget_usd": "5000.00",
        "is_us_resident": True,
        "vehicle_pref": "car",
        "vibe_tags": [],
        "max_drive_hours_per_day": "4.0",
    }
    payload.update(overrides)
    return payload


def test_featured_list_is_empty_by_default(api_client):
    _seed_spots(2)
    api_client.post("/api/plan/", _payload(), format="json")

    response = api_client.get("/api/plan/featured")

    assert response.status_code == 200
    assert response.data == []


def test_featured_list_returns_lean_teaser_for_flagged_trips(api_client):
    _seed_spots(2)
    create_response = api_client.post("/api/plan/", _payload(), format="json")
    TripRequest.objects.filter(public_id=create_response.data["id"]).update(is_featured=True)

    response = api_client.get("/api/plan/featured")

    assert response.status_code == 200
    assert len(response.data) == 1
    trip = response.data[0]
    assert trip["id"] == create_response.data["id"]
    assert trip["origin_airport"] == "JAC"
    assert trip["days"] > 0
    assert len(trip["destinations"]) > 0
    lean_total = next(
        o["cost"]["total"] for o in create_response.data["options"] if o["tier"] == "LEAN"
    )
    assert trip["from_total"] == lean_total


def test_featured_list_excludes_unflagged_trips(api_client):
    _seed_spots(2)
    api_client.post("/api/plan/", _payload(), format="json")

    assert TripRequest.objects.filter(is_featured=True).count() == 0
    response = api_client.get("/api/plan/featured")
    assert response.data == []
