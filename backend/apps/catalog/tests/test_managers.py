"""SpotQuerySet.within_drive_of() / .best_in_month()."""

import pytest

from apps.catalog.models import DriveTime, Spot
from apps.catalog.tests.factories import ClimateNormalFactory, CrowdIndexFactory, SpotFactory

pytestmark = pytest.mark.django_db


def test_within_drive_of_filters_by_origin_and_minutes():
    near = SpotFactory()
    far = SpotFactory()
    DriveTime.objects.create(origin_code="JFK", spot=near, minutes=90, miles=60)
    DriveTime.objects.create(origin_code="JFK", spot=far, minutes=300, miles=200)

    result = Spot.objects.within_drive_of("JFK", max_minutes=120)

    assert list(result) == [near]


def test_within_drive_of_ignores_other_origins():
    spot = SpotFactory()
    DriveTime.objects.create(origin_code="LAX", spot=spot, minutes=60, miles=40)

    result = Spot.objects.within_drive_of("JFK", max_minutes=120)

    assert list(result) == []


def test_best_in_month_orders_by_score_and_filters_threshold():
    good = SpotFactory()
    ClimateNormalFactory(spot=good, month=7, high_f="75.0", low_f="55.0", precip_in="0.0")
    CrowdIndexFactory(spot=good, month=7, score=10)

    bad = SpotFactory()
    ClimateNormalFactory(spot=bad, month=7, high_f="115.0", low_f="95.0", precip_in="0.0")
    CrowdIndexFactory(spot=bad, month=7, score=95)

    result = Spot.objects.best_in_month(7, min_score=60)

    assert result == [good]
