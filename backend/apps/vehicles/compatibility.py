"""vehicle_fits(spot, spec) -> Fit | Warning | Blocked."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal

WARNING_MARGIN_FT = Decimal("0.5")  # within 6 inches of a limit is worth flagging


@dataclass(frozen=True)
class VehicleLimitInput:
    """Decoupled from apps.catalog.models.VehicleLimit, same pattern as
    apps.fees.dataclasses.ParkFeeInput."""

    max_length_ft: Decimal | None
    max_height_ft: Decimal | None
    effective_from: date | None


@dataclass(frozen=True)
class FitResult:
    status: Literal["fits", "warning", "blocked"]
    reasons: list[str]


def vehicle_fits(
    length_ft: Decimal,
    height_ft: Decimal,
    limits: list[VehicleLimitInput],
    travel_date: date,
) -> FitResult:
    """Worst status across every limit that's in effect on travel_date. A limit whose
    effective_from is in the future relative to travel_date doesn't apply yet — this is
    the exact Zion-35'9"-from-7-June nuance BUILD_PROMPT §1 calls out."""
    applicable = [
        limit
        for limit in limits
        if limit.effective_from is None or limit.effective_from <= travel_date
    ]

    worst: Literal["fits", "warning", "blocked"] = "fits"
    reasons: list[str] = []

    for limit in applicable:
        status, reason = _check_one(length_ft, height_ft, limit)
        if reason:
            reasons.append(reason)
        if _rank(status) > _rank(worst):
            worst = status

    return FitResult(status=worst, reasons=reasons)


def _check_one(
    length_ft: Decimal, height_ft: Decimal, limit: VehicleLimitInput
) -> tuple[Literal["fits", "warning", "blocked"], str | None]:
    if limit.max_length_ft is not None and length_ft > limit.max_length_ft:
        return "blocked", f"Vehicle is {length_ft}ft, exceeds the {limit.max_length_ft}ft limit."
    if limit.max_height_ft is not None and height_ft > limit.max_height_ft:
        return (
            "blocked",
            f"Vehicle is {height_ft}ft tall, exceeds the {limit.max_height_ft}ft limit.",
        )

    if limit.max_length_ft is not None and limit.max_length_ft - length_ft <= WARNING_MARGIN_FT:
        return "warning", f"Vehicle length is close to the {limit.max_length_ft}ft limit."
    if limit.max_height_ft is not None and limit.max_height_ft - height_ft <= WARNING_MARGIN_FT:
        return "warning", f"Vehicle height is close to the {limit.max_height_ft}ft limit."

    return "fits", None


def _rank(status: Literal["fits", "warning", "blocked"]) -> int:
    return {"fits": 0, "warning": 1, "blocked": 2}[status]
