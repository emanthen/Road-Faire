"""eia_fuel_weekly — pre-warms apps.planner.fuel's cache. places_monthly / _refresh_spot_phone
— Places-sourced contact_phone refresh, respecting is_manually_verified."""

from unittest.mock import patch

import pytest

from apps.catalog.tests.factories import SpotFactory
from apps.ingest.clients.places import PlacesClient
from apps.ingest.tasks import _refresh_spot_phone, eia_fuel_weekly, places_monthly

pytestmark = pytest.mark.django_db


def test_calls_current_fuel_price_per_gallon():
    with patch("apps.planner.fuel.current_fuel_price_per_gallon") as mock_fn:
        eia_fuel_weekly()

    mock_fn.assert_called_once()


def test_places_monthly_noops_without_an_api_key():
    with patch("apps.ingest.tasks.settings.GOOGLE_PLACES_API_KEY", ""):
        places_monthly()  # must not touch the DB or raise — no key configured


def test_refresh_spot_phone_sets_contact_phone_from_places():
    spot = SpotFactory(name="Test Park", contact_phone="")
    client = PlacesClient(mode="replay")

    changed = _refresh_spot_phone(client, spot)

    spot.refresh_from_db()
    assert changed is True
    assert spot.contact_phone == "(307) 555-0100"


def test_refresh_spot_phone_skips_a_manually_verified_spot():
    spot = SpotFactory(
        name="Test Park", contact_phone="(555) 000-0000", is_manually_verified=True
    )
    client = PlacesClient(mode="replay")

    changed = _refresh_spot_phone(client, spot)

    spot.refresh_from_db()
    assert changed is False
    assert spot.contact_phone == "(555) 000-0000"
