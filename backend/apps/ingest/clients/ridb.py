"""Campgrounds, permits, timed entry (Recreation.gov RIDB API)."""

from django.conf import settings

from apps.ingest.clients.base import FixtureRecordingSession, RateLimiter

BASE_URL = "https://ridb.recreation.gov/api/v1"
MIN_INTERVAL_SECONDS = 0.5


class RIDBClient:
    def __init__(self, mode: str = "replay"):
        self.session = FixtureRecordingSession("ridb", mode=mode)
        self.limiter = RateLimiter(MIN_INTERVAL_SECONDS)
        self.api_key = getattr(settings, "RIDB_API_KEY", "")

    def _headers(self) -> dict:
        return {"apikey": self.api_key}

    def facilities(self, query: str) -> dict:
        """Facilities (campgrounds, permit entrances) matching a name query."""
        self.limiter.wait()
        url = f"{BASE_URL}/facilities?query={query}"
        safe_name = query.replace(" ", "_").lower()
        return self.session.get_json(url, name=f"facilities_{safe_name}", headers=self._headers())

    def permit_entrances(self, facility_id: str) -> dict:
        """Timed-entry / permit entrance details for a facility."""
        self.limiter.wait()
        url = f"{BASE_URL}/facilities/{facility_id}/permitentrances"
        return self.session.get_json(
            url, name=f"permitentrances_{facility_id}", headers=self._headers()
        )
