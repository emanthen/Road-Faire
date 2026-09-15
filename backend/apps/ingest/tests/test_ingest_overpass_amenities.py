"""ingest_overpass_amenities management command, against the recorded fixtures used by
test_overpass_client.py (lat=44.428, lon=-110.5885)."""

import pytest
from django.contrib.gis.geos import Point
from django.core.management import call_command

from apps.catalog.models import SpotAmenity
from apps.catalog.tests.factories import SpotFactory

pytestmark = pytest.mark.django_db

LAT, LON = 44.428, -110.5885


def test_ingest_creates_dump_station_and_water_rows():
    spot = SpotFactory(geom=Point(LON, LAT))

    call_command("ingest_overpass_amenities", "--mode=replay")

    assert SpotAmenity.objects.filter(spot=spot, kind=SpotAmenity.Kind.DUMP_STATION).count() == 1
    assert SpotAmenity.objects.filter(spot=spot, kind=SpotAmenity.Kind.WATER).count() == 1
    row = SpotAmenity.objects.filter(kind=SpotAmenity.Kind.WATER).first()
    assert row.needs_verification is True
    assert row.source_url == "https://www.openstreetmap.org/copyright"


def test_ingest_is_idempotent_on_rerun():
    spot = SpotFactory(geom=Point(LON, LAT))

    call_command("ingest_overpass_amenities", "--mode=replay")
    call_command("ingest_overpass_amenities", "--mode=replay")

    assert SpotAmenity.objects.filter(spot=spot).count() == 2


def test_ingest_with_no_spots_is_a_noop():
    call_command("ingest_overpass_amenities", "--mode=replay")

    assert SpotAmenity.objects.count() == 0
