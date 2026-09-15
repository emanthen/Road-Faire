"""seed_chicago_vendors management command."""

import pytest
from django.core.management import call_command

from apps.partners.models import Offer, Partner

pytestmark = pytest.mark.django_db


def test_seed_creates_three_vendors_with_no_fabricated_commission():
    call_command("seed_chicago_vendors")

    assert Partner.objects.count() == 4
    assert all(Partner.objects.values_list("needs_verification", flat=True))
    assert all(p.service_area == "Chicago, IL" for p in Partner.objects.all())
    assert set(Offer.objects.values_list("category", flat=True)) == {
        Offer.Category.CAMPERVAN,
        Offer.Category.BICYCLE,
        Offer.Category.CAMPING_GEAR,
        Offer.Category.CAR,
    }
    # No commission relationship exists with these vendors — must not claim one.
    assert all(note == "" for note in Offer.objects.values_list("commission_note", flat=True))


def test_seed_is_idempotent():
    call_command("seed_chicago_vendors")
    call_command("seed_chicago_vendors")

    assert Partner.objects.count() == 4
    assert Offer.objects.count() == 4
