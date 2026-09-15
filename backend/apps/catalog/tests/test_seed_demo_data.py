"""seed_demo_data management command."""

import pytest
from django.core.management import call_command

from apps.catalog.models import ClimateNormal, CrowdIndex, Spot
from apps.catalog.scoring import month_score

pytestmark = pytest.mark.django_db


def test_seed_creates_eleven_surcharge_parks():
    call_command("seed_demo_data")

    assert Spot.objects.count() == 11
    assert set(Spot.objects.values_list("slug", flat=True)) == {
        "acad", "brca", "ever", "glac", "grca", "grte", "romo", "seki", "yell", "yose", "zion",
    }
    assert all(Spot.objects.values_list("needs_verification", flat=True))
    assert all("[DEMO" in blurb for blurb in Spot.objects.values_list("blurb", flat=True))


def test_seed_is_idempotent():
    call_command("seed_demo_data")
    call_command("seed_demo_data")

    assert Spot.objects.count() == 11
    assert ClimateNormal.objects.count() == 11 * 12
    assert CrowdIndex.objects.count() == 11 * 12


def test_seeded_spots_score_above_planner_threshold():
    call_command("seed_demo_data")

    yellowstone = Spot.objects.get(slug="yell")
    assert month_score(yellowstone, 7) >= 60
