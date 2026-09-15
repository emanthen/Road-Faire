"""Nearest gas station and place to eat along each leg of a road trip (BUILD_PROMPT
follow-up: "add gas station when time to best fuel and where best place to eat").

ponytail: the "leg" is the straight line between two stops (same straight-line
approximation clustering.py already uses for the whole route — no real road-routing
data, per apps.catalog.DriveTime being empty). The lookup point is the leg's midpoint,
not a real point on the road. Upgrade path: once real DriveTime/road-geometry exists,
look up several points along the actual route instead of one midpoint.

Overpass is a free public API but rate-limits unregistered clients (apps.ingest.clients
.overpass.MIN_INTERVAL_SECONDS) and can be slow/unavailable — so results are cached in
Django's cache framework (keyed by rounded midpoint) for a month. A cache miss with
Overpass unreachable returns None fields rather than failing the whole plan request.
"""

from dataclasses import dataclass

import requests
from django.core.cache import cache

from apps.core.geo import haversine_miles
from apps.ingest.clients.base import RateLimiter

CACHE_TTL_SECONDS = 60 * 60 * 24 * 30  # OSM points of interest don't move day to day.
# Negative/failed lookups get a much shorter TTL — Overpass being briefly slow or down
# shouldn't poison the cache for a month once it recovers.
FAILURE_CACHE_TTL_SECONDS = 60 * 10
SEARCH_RADIUS_M = 8000
OVERPASS_QUERY_TIMEOUT_S = 10  # server-side budget, embedded in the Overpass QL itself
# (connect timeout, read timeout) — connect fails fast if the host is unreachable;
# read is generous enough to exceed OVERPASS_QUERY_TIMEOUT_S so a genuine "no results"
# reply isn't cut off before the server gives up.
HTTP_TIMEOUT_S = (5, 12)
OSM_ATTRIBUTION_URL = "https://www.openstreetmap.org/copyright"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# ponytail: a single process-wide limiter, same as apps.ingest.clients.overpass — fine
# for one web worker hitting Overpass's public rate limit; a multi-worker deployment
# would need a shared (e.g. Redis-backed) limiter instead.
_limiter = RateLimiter(min_interval_seconds=1.0)
# A plain session, deliberately with NO retry adapter (unlike apps.core.http.get_session,
# built for background ingest jobs) — this runs inside a live user-facing request, so a
# slow Overpass should fail once and fast, not retry-and-backoff for a minute.
_session = requests.Session()


@dataclass(frozen=True)
class Waypoint:
    name: str
    latitude: float
    longitude: float
    distance_mi: float


@dataclass(frozen=True)
class LegWaypoints:
    fuel: Waypoint | None
    restaurant: Waypoint | None
    source_url: str = OSM_ATTRIBUTION_URL


def _nearest(elements: list[dict], lat: float, lon: float) -> Waypoint | None:
    nodes = [e for e in elements if e.get("type") == "node" and e.get("lat") is not None]
    if not nodes:
        return None
    best = min(nodes, key=lambda n: haversine_miles(lat, lon, n["lat"], n["lon"]))
    name = best.get("tags", {}).get("name", "Unnamed")
    return Waypoint(
        name=name,
        latitude=best["lat"],
        longitude=best["lon"],
        distance_mi=round(haversine_miles(lat, lon, best["lat"], best["lon"]), 1),
    )


def leg_waypoints(lat1: float, lon1: float, lat2: float, lon2: float) -> LegWaypoints:
    mid_lat, mid_lon = (lat1 + lat2) / 2, (lon1 + lon2) / 2
    cache_key = f"leg_waypoints:{mid_lat:.3f}:{mid_lon:.3f}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    result, ttl = _fetch(mid_lat, mid_lon)
    cache.set(cache_key, result, ttl)
    return result


def _query(overpass_ql: str) -> dict:
    _limiter.wait()
    response = _session.get(OVERPASS_URL, params={"data": overpass_ql}, timeout=HTTP_TIMEOUT_S)
    response.raise_for_status()
    return response.json()


def _fetch(mid_lat: float, mid_lon: float) -> tuple[LegWaypoints, int]:
    q = f"[out:json][timeout:{OVERPASS_QUERY_TIMEOUT_S}];"
    try:
        fuel_payload = _query(
            f'{q}node["amenity"="fuel"](around:{SEARCH_RADIUS_M},{mid_lat},{mid_lon});out;'
        )
        food_payload = _query(
            f'{q}node["amenity"~"restaurant|fast_food|cafe"]'
            f"(around:{SEARCH_RADIUS_M},{mid_lat},{mid_lon});out;"
        )
    except Exception:  # noqa: BLE001 — Overpass being down shouldn't break the itinerary
        return LegWaypoints(fuel=None, restaurant=None), FAILURE_CACHE_TTL_SECONDS

    fuel = _nearest(fuel_payload.get("elements") or [], mid_lat, mid_lon)
    restaurant = _nearest(food_payload.get("elements") or [], mid_lat, mid_lon)
    return LegWaypoints(fuel=fuel, restaurant=restaurant), CACHE_TTL_SECONDS
