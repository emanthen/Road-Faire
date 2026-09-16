"""FeeSchedule versioning — a fee change ships as a new row, not a code deploy."""

from datetime import date
from decimal import Decimal

import pytest

from apps.fees.models import FeeSchedule
from apps.fees.repository import default_rates, load_fee_schedule

pytestmark = pytest.mark.django_db


def test_two_schedule_rows_with_different_effective_from_yield_different_rates():
    FeeSchedule.objects.create(
        key=FeeSchedule.Key.NONRESIDENT_SURCHARGE,
        amount=Decimal("100.00"),
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 12, 31),
        source_url="https://www.nps.gov/aboutus/entrance-fee-prices.htm",
    )
    FeeSchedule.objects.create(
        key=FeeSchedule.Key.NONRESIDENT_SURCHARGE,
        amount=Decimal("125.00"),
        effective_from=date(2027, 1, 1),
        source_url="https://www.nps.gov/aboutus/entrance-fee-prices.htm",
    )

    rates_2026 = load_fee_schedule(date(2026, 6, 1))
    rates_2027 = load_fee_schedule(date(2027, 6, 1))

    assert rates_2026.nonresident_surcharge == Decimal("100.00")
    assert rates_2027.nonresident_surcharge == Decimal("125.00")


def test_no_matching_row_falls_back_to_constants_bootstrap_value():
    rates = load_fee_schedule(date(2020, 1, 1))  # before any FeeSchedule row exists
    assert rates.nonresident_surcharge == default_rates().nonresident_surcharge


def test_same_key_two_open_ended_rows_uses_the_most_recent_effective_from():
    FeeSchedule.objects.create(
        key=FeeSchedule.Key.ATB_RESIDENT,
        amount=Decimal("80.00"),
        effective_from=date(2026, 1, 1),
    )
    FeeSchedule.objects.create(
        key=FeeSchedule.Key.ATB_RESIDENT,
        amount=Decimal("90.00"),
        effective_from=date(2027, 1, 1),
    )

    assert load_fee_schedule(date(2027, 6, 1)).atb_resident == Decimal("90.00")
