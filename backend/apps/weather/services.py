"""forecast_for(spot, date_range), normals_for(spot)."""

from datetime import date

from django.core.cache import cache

from apps.weather.clients import OpenMeteoClient

CACHE_TIMEOUT_SECONDS = 3600  # 1h, per apps.weather.clients' docstring


def forecast_for(spot, start_date: date, end_date: date, mode: str = "replay") -> list[dict]:
    """Daily forecast for a spot's date range, cached 1h per (spot, date range)."""
    cache_key = f"weather:forecast:{spot.slug}:{start_date}:{end_date}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    client = OpenMeteoClient(mode=mode)
    payload = client.forecast(spot.geom.y, spot.geom.x, start_date, end_date)
    daily = payload.get("daily", {})

    result = [
        {
            "date": day,
            "high_f": daily["temperature_2m_max"][i],
            "low_f": daily["temperature_2m_min"][i],
            "precip_in": daily["precipitation_sum"][i],
        }
        for i, day in enumerate(daily.get("time", []))
    ]

    cache.set(cache_key, result, timeout=CACHE_TIMEOUT_SECONDS)
    return result


def normals_for(spot) -> list[dict]:
    """Month-by-month climate normals already in the catalog (NOAA-sourced, Phase 2) —
    no external call, just a clean read of apps.catalog.models.ClimateNormal."""
    return [
        {
            "month": normal.month,
            "high_f": float(normal.high_f),
            "low_f": float(normal.low_f),
            "precip_in": float(normal.precip_in),
        }
        for normal in spot.climate_normals.order_by("month")
    ]
