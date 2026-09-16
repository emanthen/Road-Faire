"""Bridges the versioned, admin-editable FeeSchedule rows to the pure entry_fees() engine.

This is the only place in apps.fees that touches the ORM for rate values — engine.py stays
pure per BUILD_PROMPT §4 ("no ORM calls inside the math"). A fee change now goes live by
adding a FeeSchedule row with a future effective_from, not by editing constants.py and
redeploying.
"""

from datetime import date
from decimal import Decimal

from django.db.models import Q

from apps.fees import constants
from apps.fees.dataclasses import FeeRates
from apps.fees.models import FeeSchedule


def default_rates() -> FeeRates:
    """The constants.py bootstrap values, wrapped as FeeRates. Used as entry_fees()'s
    fallback so callers that don't care about DB versioning (most unit tests) don't need
    to construct a FeeRates by hand — real request-handling code always calls
    load_fee_schedule() instead and never relies on this default."""

    return FeeRates(
        nonresident_surcharge=constants.NONRESIDENT_SURCHARGE,
        atb_resident=constants.ATB_RESIDENT,
        atb_nonresident=constants.ATB_NONRESIDENT,
        surcharge_park_slugs=constants.SURCHARGE_PARK_SLUGS,
    )


def _amount_on(key, on_date: date, fallback: Decimal) -> Decimal:
    # `key` is a FeeSchedule.Key member — left unannotated because Django's TextChoices
    # attribute access types as tuple[str, str] to mypy without django-stubs (not
    # installed; BUILD_PROMPT §2 pins the dependency list and doesn't include it).
    row = (
        FeeSchedule.objects.filter(key=key, effective_from__lte=on_date)
        .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=on_date))
        .order_by("-effective_from")
        .first()
    )
    return row.amount if row is not None else fallback


def load_fee_schedule(on_date: date) -> FeeRates:
    """The FeeSchedule row effective on `on_date` for each key, falling back to the
    constants.py bootstrap value for any key with no row yet (e.g. before
    `seed_fee_schedule` has run). surcharge_park_slugs has no FeeSchedule row type —
    it's structural (which parks), not a versioned dollar amount — so it always comes
    from constants.py."""

    fallback = default_rates()
    return FeeRates(
        nonresident_surcharge=_amount_on(
            FeeSchedule.Key.NONRESIDENT_SURCHARGE, on_date, fallback.nonresident_surcharge
        ),
        atb_resident=_amount_on(FeeSchedule.Key.ATB_RESIDENT, on_date, fallback.atb_resident),
        atb_nonresident=_amount_on(
            FeeSchedule.Key.ATB_NONRESIDENT, on_date, fallback.atb_nonresident
        ),
        surcharge_park_slugs=fallback.surcharge_park_slugs,
    )
