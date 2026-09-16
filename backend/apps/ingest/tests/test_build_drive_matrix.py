"""build_drive_matrix — writes one DriveTime row per airport x spot pair, replaying
the same OSRM fixture apps.ingest.tests.test_osrm_client uses (origin/destination
40.0,-105.0 -> 40.5,-105.5), so no live network call happens here either."""

from unittest.mock import patch

import pytest
from django.contrib.gis.geos import Point
from django.core.management import call_command

from apps.catalog.models import DriveTime
from apps.catalog.tests.factories import SpotFactory

pytestmark = pytest.mark.django_db

FAKE_AIRPORTS = {"JAC": (40.0, -105.0)}


def test_writes_a_drive_time_row_per_airport_spot_pair():
    spot = SpotFactory(geom=Point(-105.5, 40.5))

    with (
        patch("apps.ingest.management.commands.build_drive_matrix.AIRPORTS", FAKE_AIRPORTS),
        patch("apps.ingest.clients.osrm.settings.OSRM_BASE_URL", "http://localhost:5001"),
    ):
        call_command("build_drive_matrix", mode="replay")

    drive_time = DriveTime.objects.get(origin_code="JAC", spot=spot)
    assert drive_time.minutes == 75
    assert str(drive_time.miles) == "50.0"


def test_is_safe_to_rerun():
    spot = SpotFactory(geom=Point(-105.5, 40.5))

    with (
        patch("apps.ingest.management.commands.build_drive_matrix.AIRPORTS", FAKE_AIRPORTS),
        patch("apps.ingest.clients.osrm.settings.OSRM_BASE_URL", "http://localhost:5001"),
    ):
        call_command("build_drive_matrix", mode="replay")
        call_command("build_drive_matrix", mode="replay")

    assert DriveTime.objects.filter(origin_code="JAC", spot=spot).count() == 1
