from decimal import Decimal
from typing import Literal

from apps.core.money import usd
from apps.fees.dataclasses import (
    EntryFeeBreakdown,
    EntryFeeLine,
    FeeRates,
    ParkFeeInput,
    PassRecommendation,
)
from apps.fees.explain import explain_recommendation
from apps.fees.repository import default_rates


def entry_fees(
    parks: list[ParkFeeInput],
    adults_16plus: int,
    is_us_resident: bool,
    rates: FeeRates | None = None,
    children_under_16: int = 0,
) -> EntryFeeBreakdown:
    """Pure — no ORM. `rates` is the FeeSchedule snapshot effective for this calculation;
    callers on the request path load it via apps.fees.repository.load_fee_schedule() so a
    fee change ships as a new FeeSchedule row, not a code deploy. Omitting `rates` (most
    unit tests) falls back to the constants.py bootstrap values.

    `children_under_16` is accepted but never changes a total: BUILD_PROMPT §4.2 states
    children under 16 are always free, at every park, with no per-child fee modeled
    anywhere in the system. It exists so the API can accept a party's full composition
    without the caller needing to strip children out first — see test_children.py.
    """

    rates = rates if rates is not None else default_rates()
    lines = [_line_for_park(park, adults_16plus, is_us_resident, rates) for park in parks]

    pay_as_you_go_total = usd(sum((line.subtotal for line in lines), Decimal("0")))
    annual_pass_total = usd(_annual_pass_total(adults_16plus, is_us_resident, rates))
    recommendation = _recommend(pay_as_you_go_total, annual_pass_total)

    return EntryFeeBreakdown(
        lines=lines,
        pay_as_you_go_total=pay_as_you_go_total,
        annual_pass_total=annual_pass_total,
        recommendation=recommendation,
    )


def _line_for_park(
    park: ParkFeeInput, adults_16plus: int, is_us_resident: bool, rates: FeeRates
) -> EntryFeeLine:
    if park.fee_type == "person":
        standard = park.standard_fee * adults_16plus
    else:
        standard = park.standard_fee

    if not is_us_resident and park.slug in rates.surcharge_park_slugs:
        surcharge = rates.nonresident_surcharge * adults_16plus
    else:
        surcharge = Decimal("0")

    return EntryFeeLine(
        park_name=park.name, standard_fee=usd(standard), surcharge=usd(surcharge)
    )


def _annual_pass_total(adults_16plus: int, is_us_resident: bool, rates: FeeRates) -> Decimal:
    if is_us_resident:
        return rates.atb_resident  # one pass covers the vehicle for the whole trip
    return rates.atb_nonresident * adults_16plus  # one pass per adult, to exempt each


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
    return PassRecommendation(cheaper=cheaper, savings=usd(savings), explanation=explanation)
