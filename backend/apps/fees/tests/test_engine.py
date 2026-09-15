"""Every case from BUILD_PROMPT §4.2 — 100% branch coverage target for Phase 3."""

from decimal import Decimal

from apps.fees.dataclasses import ParkFeeInput
from apps.fees.engine import entry_fees


def _park(slug: str, name: str, fee: str, fee_type: str = "vehicle") -> ParkFeeInput:
    return ParkFeeInput(slug=slug, name=name, standard_fee=Decimal(fee), fee_type=fee_type)


def test_two_nonresident_adults_three_surcharge_parks_recommends_passes():
    """Yellowstone + Grand Teton + Yosemite, 2 non-resident adults."""
    parks = [
        _park("yell", "Yellowstone", "35"),
        _park("grte", "Grand Teton", "35"),
        _park("yose", "Yosemite", "35"),
    ]

    result = entry_fees(parks, adults_16plus=2, is_us_resident=False)

    total_surcharge = sum((line.surcharge for line in result.lines), Decimal("0"))
    assert total_surcharge == Decimal("600")
    assert result.pay_as_you_go_total == Decimal("705")  # 3*35 + 600
    assert result.annual_pass_total == Decimal("500")  # 2 * 250
    assert result.recommendation.cheaper == "annual_pass"
    assert result.recommendation.savings == Decimal("205")


def test_one_nonresident_adult_one_surcharge_park_is_a_tie():
    """Constructed so pay-as-you-go ($150 fee + $100 surcharge) exactly equals one
    non-resident pass ($250) — the engine must explain the tie, not just call a winner."""
    parks = [_park("zion", "Zion", "150")]

    result = entry_fees(parks, adults_16plus=1, is_us_resident=False)

    assert result.pay_as_you_go_total == Decimal("250")
    assert result.annual_pass_total == Decimal("250")
    assert result.recommendation.cheaper == "tie"
    assert result.recommendation.savings == Decimal("0")
    assert "same" in result.recommendation.explanation.lower() or (
        "either" in result.recommendation.explanation.lower()
    )


def test_two_resident_adults_pass_only_worth_it_past_two_parks():
    """No surcharge for residents. A single $80 resident pass covers the vehicle for
    the whole trip, so it only beats pay-as-you-go once there are enough parks."""
    two_parks = [_park("carh", "Park A", "35"), _park("carh2", "Park B", "35")]
    three_parks = two_parks + [_park("carh3", "Park C", "35")]

    two_park_result = entry_fees(two_parks, adults_16plus=2, is_us_resident=True)
    three_park_result = entry_fees(three_parks, adults_16plus=2, is_us_resident=True)

    assert all(line.surcharge == Decimal("0") for line in two_park_result.lines)
    assert two_park_result.annual_pass_total == Decimal("80")
    assert two_park_result.pay_as_you_go_total == Decimal("70")
    assert two_park_result.recommendation.cheaper == "pay_as_you_go"

    assert three_park_result.pay_as_you_go_total == Decimal("105")
    assert three_park_result.recommendation.cheaper == "annual_pass"


def test_children_under_16_contribute_zero_regardless_of_count():
    parks = [_park("yell", "Yellowstone", "35")]

    no_children = entry_fees(parks, adults_16plus=2, is_us_resident=False, children_under_16=0)
    three_children = entry_fees(parks, adults_16plus=2, is_us_resident=False, children_under_16=3)

    assert no_children.pay_as_you_go_total == three_children.pay_as_you_go_total
    assert no_children.annual_pass_total == three_children.annual_pass_total


def test_resident_visiting_a_surcharge_listed_park_still_pays_no_surcharge():
    """Residency is checked before park membership (short-circuit) — exercise that path
    with a park that IS on the surcharge list, not just a non-listed one."""
    parks = [_park("zion", "Zion", "35")]

    result = entry_fees(parks, adults_16plus=2, is_us_resident=True)

    assert result.lines[0].surcharge == Decimal("0")


def test_park_outside_surcharge_list_never_surcharges_regardless_of_residency():
    parks = [_park("acad_not_a_real_code", "Not A Surcharge Park", "30")]

    resident = entry_fees(parks, adults_16plus=2, is_us_resident=True)
    nonresident = entry_fees(parks, adults_16plus=2, is_us_resident=False)

    assert resident.lines[0].surcharge == Decimal("0")
    assert nonresident.lines[0].surcharge == Decimal("0")


def test_per_person_fee_type_multiplies_by_adults_not_children():
    park = _park("test_person_fee", "Per-Person Park", "20", fee_type="person")

    result = entry_fees([park], adults_16plus=3, is_us_resident=True, children_under_16=2)

    assert result.lines[0].standard_fee == Decimal("60")  # 3 adults * $20, no children
