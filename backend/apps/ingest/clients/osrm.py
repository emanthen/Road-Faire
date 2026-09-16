"""Drive-time matrix (OSRM, fallback Google Routes).

OSRM is a self-hosted routing engine (OSRM_BASE_URL, e.g. a local Docker container) —
free but needs infrastructure nobody has to run. Google Routes is the paid fallback for
whoever doesn't want to stand up OSRM, or for when a self-hosted instance is down. Both
return the same (minutes, miles) shape so build_drive_matrix doesn't care which answered.
"""

import logging
from decimal import Decimal

from django.conf import settings

from apps.ingest.clients.base import FixtureRecordingSession, RateLimiter

GOOGLE_ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
MIN_INTERVAL_SECONDS = 0.2
METERS_PER_MILE = Decimal("1609.344")

logger = logging.getLogger(__name__)


class DriveTimeUnavailable(Exception):
    """Neither OSRM nor Google Routes produced a route for this pair — the caller
    (build_drive_matrix) skips the row rather than writing a fake one."""


class DriveTimeClient:
    def __init__(self, mode: str = "replay"):
        self.osrm_session = FixtureRecordingSession("osrm", mode=mode)
        self.routes_session = FixtureRecordingSession("google_routes", mode=mode)
        self.limiter = RateLimiter(MIN_INTERVAL_SECONDS)
        self.osrm_base_url = getattr(settings, "OSRM_BASE_URL", "")
        self.google_routes_api_key = getattr(settings, "GOOGLE_ROUTES_API_KEY", "")

    def drive_time(
        self, origin: tuple[float, float], destination: tuple[float, float]
    ) -> tuple[int, Decimal]:
        """(minutes, miles) for the driving route from `origin` to `destination`, each
        a (lat, lon) pair. Tries OSRM first; falls back to Google Routes if OSRM is
        unconfigured or fails; raises DriveTimeUnavailable if neither answers."""
        if self.osrm_base_url:
            try:
                return self._osrm(origin, destination)
            except Exception:
                logger.warning(
                    "OSRM route lookup failed; falling back to Google Routes", exc_info=True
                )

        if self.google_routes_api_key:
            try:
                return self._google_routes(origin, destination)
            except Exception:
                logger.warning("Google Routes lookup failed", exc_info=True)

        raise DriveTimeUnavailable(f"No route source available for {origin} -> {destination}")

    def _osrm(
        self, origin: tuple[float, float], destination: tuple[float, float]
    ) -> tuple[int, Decimal]:
        self.limiter.wait()
        (olat, olon), (dlat, dlon) = origin, destination
        url = f"{self.osrm_base_url}/route/v1/driving/{olon},{olat};{dlon},{dlat}"
        data = self.osrm_session.get_json(
            url, name=f"route_{olat}_{olon}_{dlat}_{dlon}", params={"overview": "false"}
        )
        routes = data.get("routes") or []
        if data.get("code") != "Ok" or not routes:
            raise DriveTimeUnavailable("OSRM returned no route")
        route = routes[0]
        return self._minutes_miles(route["duration"], route["distance"])

    def _google_routes(
        self, origin: tuple[float, float], destination: tuple[float, float]
    ) -> tuple[int, Decimal]:
        self.limiter.wait()
        (olat, olon), (dlat, dlon) = origin, destination
        body = {
            "origin": {"location": {"latLng": {"latitude": olat, "longitude": olon}}},
            "destination": {"location": {"latLng": {"latitude": dlat, "longitude": dlon}}},
            "travelMode": "DRIVE",
        }
        headers = {
            "X-Goog-Api-Key": self.google_routes_api_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters",
        }
        data = self.routes_session.post_json(
            GOOGLE_ROUTES_URL,
            name=f"route_{olat}_{olon}_{dlat}_{dlon}",
            json=body,
            headers=headers,
        )
        routes = data.get("routes") or []
        if not routes:
            raise DriveTimeUnavailable("Google Routes returned no route")
        route = routes[0]
        duration_seconds = float(str(route["duration"]).rstrip("s"))
        return self._minutes_miles(duration_seconds, route["distanceMeters"])

    @staticmethod
    def _minutes_miles(duration_seconds: float, distance_meters: float) -> tuple[int, Decimal]:
        minutes = round(duration_seconds / 60)
        miles = (Decimal(str(distance_meters)) / METERS_PER_MILE).quantize(Decimal("0.1"))
        return minutes, miles
