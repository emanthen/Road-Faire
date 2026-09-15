"""Parks, fees, alerts, hours (NPS API)."""

from django.conf import settings

from apps.ingest.clients.base import FixtureRecordingSession, RateLimiter

BASE_URL = "https://developer.nps.gov/api/v1"
# NPS asks for a modest rate; this is deliberately conservative for a low-volume ingest job.
MIN_INTERVAL_SECONDS = 0.5


class NPSClient:
    def __init__(self, mode: str = "replay"):
        self.session = FixtureRecordingSession("nps", mode=mode)
        self.limiter = RateLimiter(MIN_INTERVAL_SECONDS)
        self.api_key = getattr(settings, "NPS_API_KEY", "")

    def _headers(self) -> dict:
        return {"X-Api-Key": self.api_key}

    def park(self, park_code: str) -> dict:
        """A single park's core record (name, states, coordinates, description)."""
        self.limiter.wait()
        url = f"{BASE_URL}/parks?parkCode={park_code}"
        return self.session.get_json(url, name=f"parks_{park_code}", headers=self._headers())

    def fees(self, park_code: str) -> dict:
        """Entrance fees and passes for a park."""
        self.limiter.wait()
        url = f"{BASE_URL}/feespasses?parkCode={park_code}"
        return self.session.get_json(
            url, name=f"feespasses_{park_code}", headers=self._headers()
        )

    def alerts(self, park_code: str) -> dict:
        """Active alerts (closures, hazards) for a park."""
        self.limiter.wait()
        url = f"{BASE_URL}/alerts?parkCode={park_code}"
        return self.session.get_json(url, name=f"alerts_{park_code}", headers=self._headers())
