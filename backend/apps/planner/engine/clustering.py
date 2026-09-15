"""Build loops under max_drive_hours_per_day (BUILD_PROMPT §4 STEP 2).

ponytail: greedy nearest-neighbor route building, not an optimal TSP solve (NP-hard,
overkill for a 3-7 day trip among a handful of candidates). Builds several loops by
varying the starting candidate so budget.py has real options to rank. Upgrade path: a
real heuristic (2-opt) if loop quality becomes a problem once there's usage data to
judge it against.
"""

from datetime import date
from decimal import Decimal
from typing import Literal

from apps.catalog.models import Spot
from apps.catalog.scoring import month_score
from apps.core.geo import haversine_miles as _haversine_miles
from apps.planner.engine.candidates import AIRPORTS, AVG_DRIVE_SPEED_MPH
from apps.planner.engine.types import Loop, LoopStop, LoopStopActivity


def build_loops(
    candidates: list[Spot],
    origin_airport: str,
    trip_days: int,
    max_drive_hours_per_day: Decimal,
    start_date: date,
    max_loops: int = 5,
) -> list[Loop]:
    if not candidates:
        return []
    origin_lat, origin_lon = AIRPORTS[origin_airport]
    max_leg_miles = float(AVG_DRIVE_SPEED_MPH * max_drive_hours_per_day)

    loops = []
    for start_idx in range(min(max_loops, len(candidates))):
        loop = _build_one_loop(
            candidates, start_idx, origin_lat, origin_lon, trip_days, max_leg_miles, start_date
        )
        if loop is not None:
            loops.append(loop)
    return loops


def _build_one_loop(
    candidates: list[Spot],
    start_idx: int,
    origin_lat: float,
    origin_lon: float,
    trip_days: int,
    max_leg_miles: float,
    start_date: date,
) -> Loop | None:
    remaining = list(candidates)
    start = remaining.pop(start_idx)
    route = [start]
    current_lat, current_lon = start.geom.y, start.geom.x
    total_miles = _haversine_miles(origin_lat, origin_lon, current_lat, current_lon)

    while remaining and len(route) < trip_days:
        nearest, nearest_dist = None, None
        for spot in remaining:
            d = _haversine_miles(current_lat, current_lon, spot.geom.y, spot.geom.x)
            if d <= max_leg_miles and (nearest_dist is None or d < nearest_dist):
                nearest, nearest_dist = spot, d
        if nearest is None:
            break
        assert nearest_dist is not None  # set together with nearest, never apart
        route.append(nearest)
        remaining.remove(nearest)
        total_miles += nearest_dist
        current_lat, current_lon = nearest.geom.y, nearest.geom.x

    total_miles += _haversine_miles(current_lat, current_lon, origin_lat, origin_lon)

    nights_per_stop = _assign_nights(route, trip_days)
    if nights_per_stop is None:
        return None

    stops = [
        LoopStop(
            slug=spot.slug,
            name=spot.name,
            standard_fee=_entry_fee(spot),
            fee_type=_fee_type(spot),
            nights=nights,
            latitude=spot.geom.y,
            longitude=spot.geom.x,
            activities=_activities(spot),
        )
        for spot, nights in zip(route, nights_per_stop, strict=True)
    ]

    month = start_date.month
    scores = [month_score(spot, month) for spot in route]
    loop_month_score = round(sum(scores) / len(scores)) if scores else 0

    return Loop(
        stops=stops,
        total_miles=Decimal(str(round(total_miles, 1))),
        days=trip_days,
        month_score=loop_month_score,
    )


def _assign_nights(route: list[Spot], trip_days: int) -> list[int] | None:
    """Nights per stop, proportional to each spot's min_days, guaranteed to sum to
    trip_days and give every stop at least 1 night."""
    if len(route) > trip_days:
        return None  # can't give every stop even 1 night

    total_min_days = sum(spot.min_days for spot in route) or len(route)
    nights = []
    remaining_days = trip_days
    for i, spot in enumerate(route):
        stops_left_after_this = len(route) - i - 1
        if i == len(route) - 1:
            n = remaining_days
        else:
            share = spot.min_days / total_min_days
            n = max(1, round(trip_days * share))
            n = min(n, remaining_days - stops_left_after_this)
        nights.append(n)
        remaining_days -= n
    return nights


def _entry_fee(spot: Spot) -> Decimal:
    cost = getattr(spot, "cost", None)
    return cost.entry_vehicle if cost and cost.entry_vehicle else Decimal("0")


def _fee_type(spot: Spot) -> Literal["vehicle", "person"]:
    cost = getattr(spot, "cost", None)
    if cost and cost.entry_vehicle:
        return "vehicle"
    if cost and cost.entry_person:
        return "person"
    return "vehicle"


def _activities(spot: Spot) -> list[LoopStopActivity]:
    return [
        LoopStopActivity(name=activity.name, kind=activity.kind)
        for activity in spot.activities.all()
    ]
