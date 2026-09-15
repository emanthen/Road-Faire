"""Filter spots by radius + month_score (BUILD_PROMPT §4 STEP 1).

ponytail: "drive radius" is approximated with straight-line PostGIS geographic
distance, not real road distance — apps.catalog.DriveTime is empty (build_drive_matrix
needs OSRM or a paid Google Routes key, still unavailable). Upgrade path: once
DriveTime rows exist, swap this for Spot.objects.within_drive_of() (already built in
Phase 2, unused today for exactly this reason).
"""

from datetime import date
from decimal import Decimal

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from apps.catalog.models import Spot
from apps.catalog.scoring import month_score

# IATA code -> (lat, lon). Stable public reference data (same category as the NPS park
# codes in apps.ingest.seed_spots), not a volatile fact needing citation. Covers the
# gateway airports near the 25 seed spots — add more as the catalog grows.
AIRPORTS: dict[str, tuple[float, float]] = {
    "JAC": (43.6073, -110.7377),  # Jackson Hole, WY
    "BZN": (45.7772, -111.1530),  # Bozeman, MT
    "COD": (44.5201, -109.0245),  # Cody, WY
    "SLC": (40.7899, -111.9791),  # Salt Lake City, UT
    "DEN": (39.8561, -104.6737),  # Denver, CO
    "LAS": (36.0840, -115.1537),  # Las Vegas, NV
    "PHX": (33.4342, -112.0116),  # Phoenix, AZ
    "SEA": (47.4502, -122.3088),  # Seattle, WA
    "PDX": (45.5898, -122.5951),  # Portland, OR
    "MSO": (46.9163, -114.0906),  # Missoula, MT
    "RAP": (44.0453, -103.0574),  # Rapid City, SD
    "FAT": (36.7762, -119.7181),  # Fresno, CA (Sequoia & Kings Canyon)
}

AVG_DRIVE_SPEED_MPH = Decimal("50")  # ponytail: single flat assumption, not
# terrain/road-type aware; upgrade path is the same as above (real DriveTime data).


def candidate_spots(
    origin_airport: str,
    start_date: date,
    max_drive_hours_per_day: Decimal,
    trip_days: int,
    min_month_score: int = 60,
) -> list[Spot]:
    if origin_airport not in AIRPORTS:
        raise ValueError(f"Unknown airport code: {origin_airport!r}")
    lat, lon = AIRPORTS[origin_airport]
    origin_point = Point(lon, lat, srid=4326)

    max_radius_miles = float(AVG_DRIVE_SPEED_MPH * max_drive_hours_per_day * trip_days)

    nearby = (
        Spot.objects.annotate(distance=Distance("geom", origin_point))
        .filter(distance__lte=D(mi=max_radius_miles))
        .select_related("cost")
        .prefetch_related("activities")
        .order_by("distance")
    )

    month = start_date.month
    return [spot for spot in nearby if month_score(spot, month) >= min_month_score]
