from decimal import Decimal
from typing import Literal

from apps.fees.constants import (
    ATB_NONRESIDENT,
    ATB_RESIDENT,
    NONRESIDENT_SURCHARGE,
    SURCHARGE_PARK_SLUGS,
)
from apps.fees.dataclasses import EntryFeeBreakdown, EntryFeeLine, ParkFeeInput, PassRecommendation
from apps.fees.explain import explain_recommendation


def entry_fees(
    parks: list[ParkFeeInput],
    adults_16plus: int,
    is_us_resident: bool,
    children_under_16: int = 0,
) -> EntryFeeBreakdown:
    lines = [_line_for_park(park, adults_16plus, is_us_resident) for park in parks]

    pay_as_you_go_total = sum((line.subtotal for line in lines), Decimal("0"))
    annual_pass_total = _annual_pass_total(adults_16plus, is_us_resident)
    recommendation = _recommend(pay_as_you_go_total, annual_pass_total)

    return EntryFeeBreakdown(
        lines=lines,
        pay_as_you_go_total=pay_as_you_go_total,
        annual_pass_total=annual_pass_total,
        recommendation=recommendation,
    )


def _line_for_park(park: ParkFeeInput, adults_16plus: int, is_us_resident: bool) -> EntryFeeLine:
    if park.fee_type == "person":
        standard = park.standard_fee * adults_16plus
    else:
        standard = park.standard_fee

    if not is_us_resident and park.slug in SURCHARGE_PARK_SLUGS:
        surcharge = NONRESIDENT_SURCHARGE * adults_16plus
    else:
        surcharge = Decimal("0")

    return EntryFeeLine(park_name=park.name, standard_fee=standard, surcharge=surcharge)


def _annual_pass_total(adults_16plus: int, is_us_resident: bool) -> Decimal:
    if is_us_resident:
        return ATB_RESIDENT  # one pass covers the vehicle for the whole trip
    return ATB_NONRESIDENT * adults_16plus  # one pass per adult, to exempt each from surcharge


def _recommend(pay_as_you_go_total: Decimal, annual_pass_total: Decimal) -> PassRecommendation:
    cheaper: Literal["pay_as_you_go", "annual_pass", "tie"]
    if pay_as_you_go_total == annual_pass_total:
        cheaper = "tie"
        savings = Decimal("0")
    elif pay_as_you_go_total < annual_pass_total:
        cheaper = "pay_as_you_go"
        savings = annual_pass_total - pay_as_you_go_total
    else:
        cheaper = "annual_pass"
        savings = pay_as_you_go_total - annual_pass_total

    explanation = explain_recommendation(cheaper, pay_as_you_go_total, annual_pass_total, savings)
    return PassRecommendation(cheaper=cheaper, savings=savings, explanation=explanation)
