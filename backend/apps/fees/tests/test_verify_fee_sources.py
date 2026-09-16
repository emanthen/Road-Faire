"""verify_fee_sources — confirms stored amounts still appear on their source page,
flags what doesn't, never silently rewrites the stored figure."""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command

from apps.fees.models import FeeSchedule

pytestmark = pytest.mark.django_db


def _fake_session(page_text: str) -> MagicMock:
    session = MagicMock()
    response = MagicMock(text=page_text)
    response.raise_for_status.return_value = None
    session.get.return_value = response
    return session


def test_matching_amount_sets_verified_at():
    row = FeeSchedule.objects.create(
        key=FeeSchedule.Key.NONRESIDENT_SURCHARGE,
        amount=Decimal("100.00"),
        effective_from=date(2026, 1, 1),
        source_url="https://www.nps.gov/aboutus/entrance-fee-prices.htm",
        needs_verification=True,
    )

    with patch(
        "apps.fees.management.commands.verify_fee_sources.get_session",
        return_value=_fake_session("charge a $100 nonresident fee"),
    ):
        call_command("verify_fee_sources")

    row.refresh_from_db()
    assert row.verified_at is not None


def test_mismatched_amount_flags_needs_verification_and_exits_nonzero():
    row = FeeSchedule.objects.create(
        key=FeeSchedule.Key.ATB_RESIDENT,
        amount=Decimal("80.00"),
        effective_from=date(2026, 1, 1),
        source_url="https://www.nps.gov/planyourvisit/passes.htm",
        needs_verification=False,
        verified_at=date(2026, 1, 1),
    )

    with patch(
        "apps.fees.management.commands.verify_fee_sources.get_session",
        return_value=_fake_session("the annual pass is now $120"),
    ):
        with pytest.raises(SystemExit):
            call_command("verify_fee_sources")

    row.refresh_from_db()
    assert row.needs_verification is True
    assert row.verified_at == date(2026, 1, 1)  # not touched — no false confirmation


def test_mismatch_never_overwrites_the_stored_amount():
    row = FeeSchedule.objects.create(
        key=FeeSchedule.Key.ATB_NONRESIDENT,
        amount=Decimal("250.00"),
        effective_from=date(2026, 1, 1),
        source_url="https://www.nps.gov/planyourvisit/passes.htm",
    )

    with patch(
        "apps.fees.management.commands.verify_fee_sources.get_session",
        return_value=_fake_session("no dollar figures on this page at all"),
    ):
        with pytest.raises(SystemExit):
            call_command("verify_fee_sources")

    row.refresh_from_db()
    assert row.amount == Decimal("250.00")


def test_rows_sharing_a_url_are_fetched_once():
    FeeSchedule.objects.create(
        key=FeeSchedule.Key.ATB_RESIDENT,
        amount=Decimal("80.00"),
        effective_from=date(2026, 1, 1),
        source_url="https://www.nps.gov/planyourvisit/passes.htm",
    )
    FeeSchedule.objects.create(
        key=FeeSchedule.Key.ATB_NONRESIDENT,
        amount=Decimal("250.00"),
        effective_from=date(2026, 1, 1),
        source_url="https://www.nps.gov/planyourvisit/passes.htm",
    )
    session = _fake_session("resident pass is $80.00, non-resident pass is $250.00")

    with patch(
        "apps.fees.management.commands.verify_fee_sources.get_session", return_value=session
    ):
        call_command("verify_fee_sources")

    assert session.get.call_count == 1


def test_no_rows_with_a_source_url_is_a_clean_noop():
    call_command("verify_fee_sources")  # no rows at all — must not raise


def test_fetch_failure_is_reported_not_raised_and_other_urls_still_get_checked():
    FeeSchedule.objects.create(
        key=FeeSchedule.Key.NONRESIDENT_SURCHARGE,
        amount=Decimal("100.00"),
        effective_from=date(2026, 1, 1),
        source_url="https://www.nps.gov/down-page.htm",
    )

    session = MagicMock()
    session.get.side_effect = ConnectionError("timed out")

    with patch(
        "apps.fees.management.commands.verify_fee_sources.get_session", return_value=session
    ):
        with pytest.raises(SystemExit):
            call_command("verify_fee_sources")
