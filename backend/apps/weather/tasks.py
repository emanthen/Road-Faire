"""warm_top_spots_cache — Celery beat, warm cache for top 100 spots hourly.

No traffic/popularity metric exists yet to rank spots by, so "top 100" is just the
first 100 by name for now — a placeholder ranking, not a guess at real popularity data.
"""

from datetime import date, timedelta

from celery import shared_task

from apps.catalog.models import Spot
from apps.weather.services import forecast_for

TOP_SPOTS_LIMIT = 100


@shared_task
def warm_top_spots_cache():
    today = date.today()
    end = today + timedelta(days=6)
    for spot in Spot.objects.all()[:TOP_SPOTS_LIMIT]:
        forecast_for(spot, today, end, mode="record")
