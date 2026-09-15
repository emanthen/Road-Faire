"""seed_spot_details management command."""

import pytest
from django.core.management import call_command

from apps.catalog.models import Photo, Spot

pytestmark = pytest.mark.django_db


def test_enriches_every_demo_spot_with_real_content():
    call_command("seed_demo_data")

    call_command("seed_spot_details")

    zion = Spot.objects.get(slug="zion")
    assert zion.elevation_ft == 8726
    assert zion.highlights
    assert zion.needs_verification is True
    assert zion.source_url

    # Everglades has no confirmed natural high point — left null, not guessed.
    ever = Spot.objects.get(slug="ever")
    assert ever.elevation_ft is None
    assert ever.best_time_to_visit


def test_attaches_two_real_photos_per_spot():
    call_command("seed_demo_data")

    call_command("seed_spot_details")

    photos = Photo.objects.filter(spot__slug="yell")
    assert photos.count() == 2
    assert photos.filter(is_primary=True).count() == 1


def test_is_idempotent():
    call_command("seed_demo_data")

    call_command("seed_spot_details")
    call_command("seed_spot_details")

    assert Photo.objects.filter(spot__slug="yell").count() == 2
