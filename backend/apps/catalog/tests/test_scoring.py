"""month_score() branch coverage."""

import pytest

from apps.catalog.scoring import month_score
from apps.catalog.tests.factories import ClimateNormalFactory, CrowdIndexFactory, SpotFactory

pytestmark = pytest.mark.django_db


def test_returns_zero_with_no_climate_data():
    spot = SpotFactory()
    assert month_score(spot, 7) == 0


def test_ideal_climate_and_low_crowd_scores_high():
    spot = SpotFactory()
    ClimateNormalFactory(spot=spot, month=7, high_f="75.0", low_f="55.0", precip_in="0.0")
    CrowdIndexFactory(spot=spot, month=7, score=10)
    assert month_score(spot, 7) >= 80


def test_extreme_heat_and_high_crowd_scores_low():
    spot = SpotFactory()
    ClimateNormalFactory(spot=spot, month=7, high_f="115.0", low_f="95.0", precip_in="0.0")
    CrowdIndexFactory(spot=spot, month=7, score=95)
    assert month_score(spot, 7) < 30


def test_missing_crowd_index_defaults_to_neutral():
    spot = SpotFactory()
    ClimateNormalFactory(spot=spot, month=7, high_f="75.0", low_f="55.0", precip_in="0.0")
    # No CrowdIndex for this month — should use the 50/50 neutral fallback, not crash.
    assert month_score(spot, 7) == round(100 * 0.6 + 50 * 0.4)


def test_high_precipitation_penalizes_score():
    spot = SpotFactory()
    ClimateNormalFactory(spot=spot, month=11, high_f="75.0", low_f="55.0", precip_in="6.0")
    CrowdIndexFactory(spot=spot, month=11, score=10)
    dry_score = month_score(spot, 11)

    spot2 = SpotFactory()
    ClimateNormalFactory(spot=spot2, month=11, high_f="75.0", low_f="55.0", precip_in="0.0")
    CrowdIndexFactory(spot=spot2, month=11, score=10)
    no_rain_score = month_score(spot2, 11)

    assert dry_score < no_rain_score
