"""DriveTimeClient — OSRM primary, Google Routes fallback, both replayed from fixtures."""

from decimal import Decimal
from unittest.mock import patch

import pytest

from apps.ingest.clients.osrm import DriveTimeClient, DriveTimeUnavailable

ORIGIN = (40.0, -105.0)
DESTINATION = (40.5, -105.5)

FALLBACK_ORIGIN = (41.0, -106.0)
FALLBACK_DESTINATION = (41.5, -106.5)


def test_uses_osrm_when_configured():
    with patch("apps.ingest.clients.osrm.settings.OSRM_BASE_URL", "http://localhost:5001"):
        client = DriveTimeClient(mode="replay")
        minutes, miles = client.drive_time(ORIGIN, DESTINATION)

    assert minutes == 75
    assert miles == Decimal("50.0")


def test_falls_back_to_google_routes_when_osrm_unconfigured():
    with (
        patch("apps.ingest.clients.osrm.settings.OSRM_BASE_URL", ""),
        patch("apps.ingest.clients.osrm.settings.GOOGLE_ROUTES_API_KEY", "test-key"),
    ):
        client = DriveTimeClient(mode="replay")
        minutes, miles = client.drive_time(FALLBACK_ORIGIN, FALLBACK_DESTINATION)

    assert minutes == 75
    assert miles == Decimal("50.0")


def test_raises_when_neither_source_is_configured():
    with (
        patch("apps.ingest.clients.osrm.settings.OSRM_BASE_URL", ""),
        patch("apps.ingest.clients.osrm.settings.GOOGLE_ROUTES_API_KEY", ""),
    ):
        client = DriveTimeClient(mode="replay")
        with pytest.raises(DriveTimeUnavailable):
            client.drive_time(ORIGIN, DESTINATION)


def test_falls_back_to_google_routes_when_osrm_call_fails():
    """OSRM configured but unreachable (no fixture for this pair) — falls through to
    Google Routes rather than propagating the OSRM error."""
    with (
        patch("apps.ingest.clients.osrm.settings.OSRM_BASE_URL", "http://localhost:5001"),
        patch("apps.ingest.clients.osrm.settings.GOOGLE_ROUTES_API_KEY", "test-key"),
    ):
        client = DriveTimeClient(mode="replay")
        minutes, miles = client.drive_time(FALLBACK_ORIGIN, FALLBACK_DESTINATION)

    assert minutes == 75
    assert miles == Decimal("50.0")
