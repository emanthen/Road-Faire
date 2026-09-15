"""Zion 35'9" limit case."""

from datetime import date
from decimal import Decimal

from apps.vehicles.compatibility import VehicleLimitInput, vehicle_fits

# BUILD_PROMPT §1: Zion applies large-vehicle limits (35 ft 9 in long, 11 ft 4 in tall)
# from 7 June 2026. 35'9" == 35.75ft, 11'4" == 11.33ft (rounded).
ZION_LIMIT = VehicleLimitInput(
    max_length_ft=Decimal("35.75"),
    max_height_ft=Decimal("11.33"),
    effective_from=date(2026, 6, 7),
)


def test_oversized_vehicle_blocked_after_zion_limit_takes_effect():
    result = vehicle_fits(
        length_ft=Decimal("36"),
        height_ft=Decimal("10"),
        limits=[ZION_LIMIT],
        travel_date=date(2026, 7, 1),
    )
    assert result.status == "blocked"
    assert result.reasons


def test_same_oversized_vehicle_fits_before_zion_limit_takes_effect():
    result = vehicle_fits(
        length_ft=Decimal("36"),
        height_ft=Decimal("10"),
        limits=[ZION_LIMIT],
        travel_date=date(2026, 5, 1),
    )
    assert result.status == "fits"


def test_comfortably_undersized_vehicle_fits():
    result = vehicle_fits(
        length_ft=Decimal("22"),
        height_ft=Decimal("9"),
        limits=[ZION_LIMIT],
        travel_date=date(2026, 7, 1),
    )
    assert result.status == "fits"


def test_vehicle_within_six_inches_of_limit_warns():
    result = vehicle_fits(
        length_ft=Decimal("35.4"),  # 35'9" - 4" = within the 6" warning margin
        height_ft=Decimal("9"),
        limits=[ZION_LIMIT],
        travel_date=date(2026, 7, 1),
    )
    assert result.status == "warning"


def test_worst_status_wins_across_multiple_limits():
    lenient = VehicleLimitInput(
        max_length_ft=Decimal("40"), max_height_ft=Decimal("13"), effective_from=None
    )
    result = vehicle_fits(
        length_ft=Decimal("36"),
        height_ft=Decimal("10"),
        limits=[lenient, ZION_LIMIT],
        travel_date=date(2026, 7, 1),
    )
    assert result.status == "blocked"


def test_no_limits_means_fits():
    result = vehicle_fits(
        length_ft=Decimal("40"), height_ft=Decimal("13"), limits=[], travel_date=date(2026, 7, 1)
    )
    assert result.status == "fits"
