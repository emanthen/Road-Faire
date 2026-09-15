"""GET /api/content/settings — staff-editable branding, defaults when unset."""

import pytest

from apps.content.models import SiteSettings

pytestmark = pytest.mark.django_db


def test_returns_defaults_when_no_row_exists(api_client):
    response = api_client.get("/api/content/settings")

    assert response.status_code == 200
    assert response.data["site_name"] == "Roadfare"


def test_returns_the_staff_edited_row(api_client):
    SiteSettings.objects.create(site_name="Roadfare Trips", tagline="Real costs, real fast.")

    response = api_client.get("/api/content/settings")

    assert response.data["site_name"] == "Roadfare Trips"
    assert response.data["tagline"] == "Real costs, real fast."
