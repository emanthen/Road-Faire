"""seed_fee_schedule management command."""

import pytest
from django.core.management import call_command

from apps.fees.models import FeeSchedule

pytestmark = pytest.mark.django_db


def test_seed_creates_one_row_per_key():
    call_command("seed_fee_schedule")

    assert FeeSchedule.objects.count() == 3
    assert set(FeeSchedule.objects.values_list("key", flat=True)) == {
        FeeSchedule.Key.NONRESIDENT_SURCHARGE,
        FeeSchedule.Key.ATB_RESIDENT,
        FeeSchedule.Key.ATB_NONRESIDENT,
    }
    assert all(FeeSchedule.objects.values_list("needs_verification", flat=True))


def test_seed_is_idempotent():
    call_command("seed_fee_schedule")
    call_command("seed_fee_schedule")

    assert FeeSchedule.objects.count() == 3
