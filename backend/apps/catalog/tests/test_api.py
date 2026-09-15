"""Spot list/detail/filter/geo-bbox endpoint behavior."""

import pytest

from apps.catalog.models import Activity, Photo
from apps.catalog.tests.factories import SpotCostFactory, SpotFactory

pytestmark = pytest.mark.django_db


def test_list_returns_spots(api_client):
    SpotFactory(name="Alpha Spot")
    SpotFactory(name="Beta Spot")

    response = api_client.get("/api/spots/")

    assert response.status_code == 200
    names = {row["name"] for row in response.data["results"]}
    assert names == {"Alpha Spot", "Beta Spot"}


def test_detail_includes_cost(api_client):
    spot = SpotFactory(name="Detail Spot")
    SpotCostFactory(spot=spot, entry_vehicle="35.00")

    response = api_client.get(f"/api/spots/{spot.slug}/")

    assert response.status_code == 200
    assert response.data["cost"]["entry_vehicle"] == "35.00"


def test_list_returns_state_abbreviation_not_id(api_client):
    spot = SpotFactory()

    response = api_client.get("/api/spots/")

    row = next(r for r in response.data["results"] if r["slug"] == spot.slug)
    assert row["state"] == spot.state.abbreviation


def test_filter_by_state(api_client):
    match = SpotFactory()
    other = SpotFactory()

    response = api_client.get(f"/api/spots/?state={match.state.abbreviation}")

    slugs = {row["slug"] for row in response.data["results"]}
    assert match.slug in slugs
    assert other.slug not in slugs


def test_filter_by_activity(api_client):
    with_trail = SpotFactory()
    Activity.objects.create(spot=with_trail, name="Rim Trail", kind=Activity.Kind.TRAIL)
    without_trail = SpotFactory()

    response = api_client.get("/api/spots/?activity=trail")

    slugs = {row["slug"] for row in response.data["results"]}
    assert with_trail.slug in slugs
    assert without_trail.slug not in slugs


def test_detail_includes_photos_and_content_fields(api_client):
    spot = SpotFactory(
        name="Gallery Spot",
        elevation_ft=8500,
        best_time_to_visit="Late May through September",
        highlights="Granite peaks and alpine lakes.",
    )
    Photo.objects.create(
        spot=spot,
        source="nps.gov",
        credit="National Park Service",
        license="Public domain",
        s3_key="/images/parks/example.jpg",
        alt_text="A lake beneath granite peaks",
        is_primary=True,
    )

    response = api_client.get(f"/api/spots/{spot.slug}/")

    assert response.status_code == 200
    assert response.data["elevation_ft"] == 8500
    assert response.data["best_time_to_visit"] == "Late May through September"
    assert len(response.data["photos"]) == 1
    assert response.data["photos"][0]["url"] == "/images/parks/example.jpg"
    assert response.data["photos"][0]["is_primary"] is True


def test_bbox_requires_valid_format(api_client):
    response = api_client.get("/api/spots/bbox/?bbox=not-a-bbox")

    assert response.status_code == 400
    assert "bbox" in response.data["error"]["detail"]


def test_bbox_returns_spots_within_box(api_client):
    inside = SpotFactory()  # default geom: (-110.5885, 44.4280)

    response = api_client.get("/api/spots/bbox/?bbox=-111,44,-110,45")

    slugs = {row["slug"] for row in response.data}
    assert inside.slug in slugs
