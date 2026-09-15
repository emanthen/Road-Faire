"""Trails, dump stations, water (OpenStreetMap/Overpass).

No API key needed — Overpass is a free public API, unlike Places (paid) and OSRM
(self-hosted), which is why this connector is real while those two stay stubs.
"""

from apps.ingest.clients.base import FixtureRecordingSession, RateLimiter

BASE_URL = "https://overpass-api.de/api/interpreter"
# Overpass's public instance asks for a conservative request rate from unregistered
# clients — this is deliberately cautious for a low-volume ingest job.
MIN_INTERVAL_SECONDS = 2.0


class OverpassClient:
    def __init__(self, mode: str = "replay"):
        self.session = FixtureRecordingSession("overpass", mode=mode)
        self.limiter = RateLimiter(MIN_INTERVAL_SECONDS)

    def trails_near(self, lat: float, lon: float, radius_m: int = 5000) -> dict:
        query = f"""
        [out:json][timeout:25];
        (
          way["highway"="path"](around:{radius_m},{lat},{lon});
          way["highway"="track"](around:{radius_m},{lat},{lon});
        );
        out geom;
        """
        return self._query(query, name=f"trails_{lat}_{lon}")

    def dump_stations_near(self, lat: float, lon: float, radius_m: int = 20000) -> dict:
        query = f"""
        [out:json][timeout:25];
        node["amenity"="sanitary_dump_station"](around:{radius_m},{lat},{lon});
        out;
        """
        return self._query(query, name=f"dump_stations_{lat}_{lon}")

    def water_near(self, lat: float, lon: float, radius_m: int = 5000) -> dict:
        query = f"""
        [out:json][timeout:25];
        node["amenity"="drinking_water"](around:{radius_m},{lat},{lon});
        out;
        """
        return self._query(query, name=f"water_{lat}_{lon}")

    def _query(self, query: str, name: str) -> dict:
        self.limiter.wait()
        return self.session.get_json(BASE_URL, name=name, params={"data": query})
