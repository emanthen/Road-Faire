"""load_rate_range — real RateCard row wins, no row falls back to the assumption band."""

from decimal import Decimal

import pytest

from apps.planner.models import RateCard
from apps.planner.rates import FALLBACK_BANDS, load_rate_range

pytestmark = pytest.mark.django_db


def test_no_row_falls_back_to_the_assumption_band_flagged_as_estimate():
    rate = load_rate_range("WY", 7, "campsite")

    assert rate == FALLBACK_BANDS["campsite"]
    assert rate.is_estimate is True


def test_real_row_wins_and_is_not_flagged_as_estimate():
    RateCard.objects.create(
        region="WY",
        month=7,
        category=RateCard.Category.CAMPSITE,
        low=Decimal("28.00"),
        high=Decimal("42.00"),
        source_url="https://example.com/wy-campsites",
    )

    rate = load_rate_range("WY", 7, "campsite")

    assert rate.low == Decimal("28.00")
    assert rate.high == Decimal("42.00")
    assert rate.is_estimate is False
    assert rate.source_url == "https://example.com/wy-campsites"


def test_row_scoped_to_region_and_month_does_not_leak_to_others():
    RateCard.objects.create(
        region="WY", month=7, category=RateCard.Category.CAMPSITE,
        low=Decimal("28.00"), high=Decimal("42.00"),
    )

    assert load_rate_range("WY", 8, "campsite").is_estimate is True  # different month
    assert load_rate_range("CO", 7, "campsite").is_estimate is True  # different region


def test_empty_region_never_hits_the_database():
    rate = load_rate_range("", 7, "campsite")

    assert rate.is_estimate is True


def test_midpoint():
    rate = FALLBACK_BANDS["motel"]
    assert rate.midpoint == (rate.low + rate.high) / 2
