"""1/2/3+ adults across 1/2/3 surcharge parks."""

from decimal import Decimal

import pytest

from apps.fees.dataclasses import ParkFeeInput
from apps.fees.engine import entry_fees

PARK_FEE = Decimal("35")


def _parks(count: int) -> list[ParkFeeInput]:
    slugs = ["yell", "grte", "yose"]
    return [
        ParkFeeInput(slug=slugs[i], name=slugs[i], standard_fee=PARK_FEE) for i in range(count)
    ]


@pytest.mark.parametrize("adults", [1, 2, 3])
@pytest.mark.parametrize("park_count", [1, 2, 3])
def test_nonresident_surcharge_scales_with_adults_and_parks(adults, park_count):
    result = entry_fees(_parks(park_count), adults_16plus=adults, is_us_resident=False)

    total_surcharge = sum((line.surcharge for line in result.lines), Decimal("0"))
    assert total_surcharge == Decimal("100") * adults * park_count
    assert result.annual_pass_total == Decimal("250") * adults


@pytest.mark.parametrize("adults", [1, 2, 3])
@pytest.mark.parametrize("park_count", [1, 2, 3])
def test_resident_never_surcharges_and_pass_is_flat(adults, park_count):
    result = entry_fees(_parks(park_count), adults_16plus=adults, is_us_resident=True)

    assert all(line.surcharge == Decimal("0") for line in result.lines)
    assert result.annual_pass_total == Decimal("80")  # flat regardless of party size
