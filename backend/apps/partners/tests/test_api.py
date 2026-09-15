"""GET /api/partners/ — read-only vendor listing."""

import pytest
from django.core.management import call_command

pytestmark = pytest.mark.django_db


def test_seeded_vendors_are_served_by_the_partners_api(api_client):
    call_command("seed_chicago_vendors")

    response = api_client.get("/api/partners/")

    assert response.status_code == 200
    names = {p["name"] for p in response.data}
    assert "Bike and Roll Chicago" in names
    partner = next(p for p in response.data if p["slug"] == "bike-and-roll-chicago")
    assert partner["offers"][0]["category"] == "bicycle"
