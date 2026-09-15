from datetime import date
from decimal import Decimal

import pytest
from django.contrib.gis.geos import Point

from apps.catalog.tests.factories import ClimateNormalFactory, CrowdIndexFactory, SpotFactory
from apps.planner.engine.candidates import AIRPORTS, candidate_spots

pytestmark = pytest.mark.django_db

JAC_LAT, JAC_LON = AIRPORTS["JAC"]


def _good_month(spot, month=7):
    ClimateNormalFactory(spot=spot, month=month, high_f="75.0", low_f="55.0", precip_in="0.0")
    CrowdIndexFactory(spot=spot, month=month, score=10)


def test_unknown_airport_raises():
    with pytest.raises(ValueError):
        candidate_spots("ZZZ", date(2026, 7, 1), Decimal("4"), 3)


def test_nearby_spot_within_radius_is_included():
    near = SpotFactory(geom=Point(JAC_LON + 0.1, JAC_LAT + 0.1))
    _good_month(near)

    result = candidate_spots("JAC", date(2026, 7, 1), Decimal("4"), 3)

    assert near in result


def test_far_spot_outside_radius_is_excluded():
    # ~50mph * 4h * 3days = 600mi radius; put this spot ~2000mi away.
    far = SpotFactory(geom=Point(JAC_LON + 25, JAC_LAT))
    _good_month(far)

    result = candidate_spots("JAC", date(2026, 7, 1), Decimal("4"), 3)

    assert far not in result


def test_low_month_score_excludes_spot():
    spot = SpotFactory(geom=Point(JAC_LON + 0.1, JAC_LAT + 0.1))
    ClimateNormalFactory(spot=spot, month=7, high_f="115.0", low_f="95.0", precip_in="0.0")
    CrowdIndexFactory(spot=spot, month=7, score=95)

    result = candidate_spots("JAC", date(2026, 7, 1), Decimal("4"), 3)

    assert spot not in result


def test_no_climate_data_excludes_spot():
    spot = SpotFactory(geom=Point(JAC_LON + 0.1, JAC_LAT + 0.1))
    # No ClimateNormal/CrowdIndex created -> month_score() returns 0.

    result = candidate_spots("JAC", date(2026, 7, 1), Decimal("4"), 3)

    assert spot not in result
