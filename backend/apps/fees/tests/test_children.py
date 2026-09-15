"""Under-16 free, mixed parties."""

from decimal import Decimal

from apps.fees.dataclasses import ParkFeeInput
from apps.fees.engine import entry_fees


def test_children_do_not_change_vehicle_fee_total():
    park = ParkFeeInput(slug="yell", name="Yellowstone", standard_fee=Decimal("35"))

    two_adults = entry_fees([park], adults_16plus=2, is_us_resident=False, children_under_16=0)
    two_adults_four_kids = entry_fees(
        [park], adults_16plus=2, is_us_resident=False, children_under_16=4
    )

    assert two_adults.pay_as_you_go_total == two_adults_four_kids.pay_as_you_go_total


def test_children_do_not_change_per_person_fee_total():
    park = ParkFeeInput(
        slug="yell", name="Yellowstone", standard_fee=Decimal("20"), fee_type="person"
    )

    result = entry_fees([park], adults_16plus=2, is_us_resident=True, children_under_16=5)

    assert result.lines[0].standard_fee == Decimal("40")  # 2 adults only


def test_children_do_not_change_surcharge_total():
    park = ParkFeeInput(slug="zion", name="Zion", standard_fee=Decimal("35"))

    result = entry_fees([park], adults_16plus=3, is_us_resident=False, children_under_16=2)

    assert result.lines[0].surcharge == Decimal("300")  # 3 adults, not 5
