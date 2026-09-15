"""month_score(spot, month) from climate + crowd + closures.

Closures aren't modeled yet — that needs an Alert/closure record sourced from NPS's
`.alerts()` endpoint, which is out of this phase's scope (see PROJECT_STRUCTURE.md's
ingest/clients/nps.py). Scoring is climate + crowd only until that model exists; a
closed-park case currently just falls through to whatever climate+crowd says, which is
wrong but not silently pretended-correct.
"""

from apps.catalog.models import ClimateNormal, Spot

IDEAL_LOW_F = 55
IDEAL_HIGH_F = 80
CLIMATE_WEIGHT = 0.6
CROWD_WEIGHT = 0.4


def _climate_comfort(normal: ClimateNormal) -> float:
    """0-100: 100 when the average of high/low sits in the ideal band, penalized by
    distance outside it and by precipitation."""
    avg = float(normal.high_f + normal.low_f) / 2
    if avg < IDEAL_LOW_F:
        temp_score = max(0.0, 100 - (IDEAL_LOW_F - avg) * 3)
    elif avg > IDEAL_HIGH_F:
        temp_score = max(0.0, 100 - (avg - IDEAL_HIGH_F) * 3)
    else:
        temp_score = 100.0
    precip_penalty = min(40.0, float(normal.precip_in) * 8)
    return max(0.0, temp_score - precip_penalty)


def month_score(spot: Spot, month: int) -> int:
    """Weighted 0-100 score for how good `month` is to visit `spot`.

    60% climate comfort (temperate 55-80F average, penalized by precipitation),
    40% inverse crowd (100 - CrowdIndex.score, so a quiet month scores higher).
    Returns 0 if there's no ClimateNormal for the month at all — we don't guess at a
    rating we can't back with data.
    """
    normal = spot.climate_normals.filter(month=month).first()
    if normal is None:
        return 0

    climate = _climate_comfort(normal)

    crowd_index = spot.crowd_indexes.filter(month=month).first()
    crowd = 100 - crowd_index.score if crowd_index else 50.0

    return round(climate * CLIMATE_WEIGHT + crowd * CROWD_WEIGHT)
