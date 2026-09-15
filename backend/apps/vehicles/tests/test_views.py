"""POST /api/vehicles/size-check contract."""

import pytest

from apps.catalog.models import VehicleLimit
from apps.catalog.tests.factories import SpotFactory
from apps.vehicles.models import VehicleClass, VehicleSpec

pytestmark = pytest.mark.django_db


def _spot_with_limit(max_length_ft="24.00", max_height_ft="10.00"):
    spot = SpotFactory()
    VehicleLimit.objects.create(
        spot=spot, max_length_ft=max_length_ft, max_height_ft=max_height_ft
    )
    return spot


def _payload(**overrides):
    payload = {
        "length_ft": "20.00",
        "height_ft": "9.00",
        "spot_slug": "",
        "travel_date": "2026-07-01",
    }
    payload.update(overrides)
    return payload


def test_size_check_with_raw_dimensions_fits(api_client):
    spot = _spot_with_limit()

    response = api_client.post(
        "/api/vehicles/size-check", _payload(spot_slug=spot.slug), format="json"
    )

    assert response.status_code == 200
    assert response.data["status"] == "fits"


def test_size_check_with_raw_dimensions_blocked(api_client):
    spot = _spot_with_limit(max_length_ft="24.00")

    response = api_client.post(
        "/api/vehicles/size-check",
        _payload(spot_slug=spot.slug, length_ft="30.00"),
        format="json",
    )

    assert response.status_code == 200
    assert response.data["status"] == "blocked"
    assert response.data["reasons"]


def test_size_check_with_vehicle_spec_id(api_client):
    spot = _spot_with_limit()
    vehicle_class = VehicleClass.objects.create(name="Class B")
    spec = VehicleSpec.objects.create(
        vehicle_class=vehicle_class,
        name="Test Van",
        length_ft="19.00",
        height_ft="9.00",
        mpg="18.0",
        sleeps=2,
        included_miles_per_night=100,
        overage_rate_per_mile="0.45",
        base_nightly_rate="150.00",
        prep_fee="0.00",
        insurance_per_night="0.00",
        one_way_fee="0.00",
        generator_rate_per_hour="0.00",
        hookup_premium_per_night="0.00",
    )

    response = api_client.post(
        "/api/vehicles/size-check",
        {
            "vehicle_spec_id": spec.id,
            "spot_slug": spot.slug,
            "travel_date": "2026-07-01",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["status"] == "fits"


def test_size_check_rejects_both_spec_and_dimensions(api_client):
    spot = _spot_with_limit()

    response = api_client.post(
        "/api/vehicles/size-check",
        _payload(spot_slug=spot.slug, vehicle_spec_id=1),
        format="json",
    )

    assert response.status_code == 400


def test_size_check_rejects_neither_spec_nor_dimensions(api_client):
    spot = _spot_with_limit()

    response = api_client.post(
        "/api/vehicles/size-check",
        {"spot_slug": spot.slug, "travel_date": "2026-07-01"},
        format="json",
    )

    assert response.status_code == 400


def test_true_cost_computes_base_and_mileage_overage(api_client):
    response = api_client.post(
        "/api/vehicles/true-cost",
        {
            "nights": 4,
            "planned_miles": "600",
            "base_nightly_rate": "150.00",
            "included_miles_per_night": 100,
            "overage_rate_per_mile": "0.45",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["base"] == "600.00"
    assert response.data["mileage_overage"] == "90.00"
    assert response.data["total"] == "690.00"


def test_true_cost_rejects_negative_rate(api_client):
    response = api_client.post(
        "/api/vehicles/true-cost",
        {"nights": 4, "planned_miles": "600", "base_nightly_rate": "-1"},
        format="json",
    )

    assert response.status_code == 400
