"""seed_rate_cards — aggregates real SpotCost.campsite_low/high into RateCard rows."""

from decimal import Decimal

import pytest
from django.core.management import call_command

from apps.catalog.tests.factories import SpotCostFactory, SpotFactory, StateFactory
from apps.planner.models import RateCard

pytestmark = pytest.mark.django_db


def test_seeds_one_row_per_state_per_month():
    wy = StateFactory(abbreviation="WY")
    SpotCostFactory(
        spot=SpotFactory(state=wy), campsite_low="25.00", campsite_high="35.00"
    )

    call_command("seed_rate_cards")

    rows = RateCard.objects.filter(region="WY", category=RateCard.Category.CAMPSITE)
    assert rows.count() == 12
    assert {r.month for r in rows} == set(range(1, 13))
    assert all(r.low == Decimal("25.00") and r.high == Decimal("35.00") for r in rows)


def test_aggregates_min_low_and_max_high_across_spots_in_the_same_state():
    wy = StateFactory(abbreviation="WY")
    SpotCostFactory(spot=SpotFactory(state=wy), campsite_low="20.00", campsite_high="30.00")
    SpotCostFactory(spot=SpotFactory(state=wy), campsite_low="25.00", campsite_high="45.00")

    call_command("seed_rate_cards")

    row = RateCard.objects.get(region="WY", month=1, category=RateCard.Category.CAMPSITE)
    assert row.low == Decimal("20.00")
    assert row.high == Decimal("45.00")


def test_spots_missing_campsite_range_are_skipped():
    SpotCostFactory(campsite_low=None, campsite_high=None)

    call_command("seed_rate_cards")

    assert RateCard.objects.count() == 0


def test_is_idempotent():
    wy = StateFactory(abbreviation="WY")
    SpotCostFactory(spot=SpotFactory(state=wy), campsite_low="25.00", campsite_high="35.00")

    call_command("seed_rate_cards")
    call_command("seed_rate_cards")

    assert RateCard.objects.filter(region="WY").count() == 12
