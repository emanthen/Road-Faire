"""POST /api/plan/, GET /api/plan/<uuid> contract."""


import pytest
from django.contrib.gis.geos import Point

from apps.catalog.models import Activity
from apps.catalog.tests.factories import (
    ClimateNormalFactory,
    CrowdIndexFactory,
    SpotCostFactory,
    SpotFactory,
)
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


def test_create_plan_returns_three_tier_options(api_client):
    _seed_spots(2)

    response = api_client.post("/api/plan/", _payload(), format="json")

    assert response.status_code == 201
    assert [o["tier"] for o in response.data["options"]] == ["LEAN", "BALANCED", "COMFORT"]
    assert response.data["id"]


def test_create_plan_echoes_the_request_summary(api_client):
    _seed_spots(2)

    create_response = api_client.post(
        "/api/plan/", _payload(vehicle_pref="van", adults=3, children=1), format="json"
    )
    plan_id = create_response.data["id"]
    get_response = api_client.get(f"/api/plan/{plan_id}")

    for response in (create_response, get_response):
        assert response.data["request"]["origin_airport"] == "JAC"
        assert response.data["request"]["vehicle_pref"] == "van"
        assert response.data["request"]["adults"] == 3
        assert response.data["request"]["children"] == 1


def test_create_plan_persists_and_is_retrievable(api_client):
    _seed_spots(2)

    create_response = api_client.post("/api/plan/", _payload(), format="json")
    plan_id = create_response.data["id"]

    assert TripRequest.objects.filter(public_id=plan_id).exists()

    get_response = api_client.get(f"/api/plan/{plan_id}")

    assert get_response.status_code == 200
    assert [o["tier"] for o in get_response.data["options"]] == ["LEAN", "BALANCED", "COMFORT"]
    # Total cost round-trips exactly through persistence.
    fetched_total = get_response.data["options"][0]["cost"]["total"]
    created_total = create_response.data["options"][0]["cost"]["total"]
    assert fetched_total == created_total

    # loop.days is the trip's calendar length, not its stop count — with 2 seeded
    # spots and a 3-day trip these differ, which is exactly what would catch a
    # regression to counting ItineraryDay rows (one per stop, not per day) on refetch.
    fetched_days = get_response.data["options"][0]["loop"]["days"]
    created_days = create_response.data["options"][0]["loop"]["days"]
    assert fetched_days == created_days
    assert fetched_days != len(get_response.data["options"][0]["loop"]["stops"])


def test_create_plan_404s_when_nothing_fits_budget(api_client):
    _seed_spots(2)

    response = api_client.post("/api/plan/", _payload(budget_usd="1.00"), format="json")

    assert response.status_code == 404


def test_create_plan_rejects_unknown_airport(api_client):
    response = api_client.post("/api/plan/", _payload(origin_airport="ZZZ"), format="json")

    assert response.status_code == 400


def test_create_plan_rejects_end_date_before_start_date(api_client):
    response = api_client.post(
        "/api/plan/", _payload(start_date="2026-07-10", end_date="2026-07-05"), format="json"
    )

    assert response.status_code == 400


def test_get_plan_404s_for_unknown_id(api_client):
    response = api_client.get("/api/plan/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


def test_get_plan_pdf_returns_pdf_bytes(api_client):
    _seed_spots(2)
    create_response = api_client.post("/api/plan/", _payload(), format="json")
    plan_id = create_response.data["id"]

    response = api_client.get(f"/api/plan/{plan_id}/pdf")

    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_get_plan_pdf_404s_for_unknown_id(api_client):
    response = api_client.get("/api/plan/00000000-0000-0000-0000-000000000000/pdf")

    assert response.status_code == 404


def test_stops_include_fee_and_activities_on_create_and_refetch(api_client):
    spot = SpotFactory(geom=Point(JAC_LON, JAC_LAT), min_days=1)
    ClimateNormalFactory(spot=spot, month=7, high_f="75.0", low_f="55.0", precip_in="0.0")
    CrowdIndexFactory(spot=spot, month=7, score=10)
    SpotCostFactory(spot=spot, entry_vehicle="35.00")
    Activity.objects.create(spot=spot, name="Rim Trail", kind=Activity.Kind.TRAIL)

    create_response = api_client.post("/api/plan/", _payload(), format="json")
    plan_id = create_response.data["id"]

    for response in (create_response, api_client.get(f"/api/plan/{plan_id}")):
        stop = response.data["options"][0]["loop"]["stops"][0]
        assert stop["standard_fee"] == "35.00"
        assert stop["fee_type"] == "vehicle"
        assert stop["activities"] == [{"name": "Rim Trail", "kind": "trail"}]
