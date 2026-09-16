"""usd() rounding — the boundary case is the one that matters."""

from decimal import Decimal

from apps.core.money import usd


def test_quantizes_to_two_decimal_places():
    assert usd(Decimal("19.444444444444444444444444444")) == Decimal("19.44")


def test_round_half_up_at_the_half_cent_boundary():
    assert usd(Decimal("1.005")) == Decimal("1.01")
    assert usd(Decimal("1.015")) == Decimal("1.02")


def test_exact_values_are_unchanged():
    assert usd(Decimal("70.00")) == Decimal("70.00")
