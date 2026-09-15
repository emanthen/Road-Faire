"""OpenMeteoClient (forecast), cached 1h.

No API key needed — Open-Meteo's forecast API is free and open, same category as
Overpass. The 1h cache lives in services.py (this client is the raw API wrapper,
fixture-recordable for tests, same pattern as apps.ingest's clients).
"""

from datetime import date

from apps.ingest.clients.base import FixtureRecordingSession, RateLimiter

BASE_URL = "https://api.open-meteo.com/v1/forecast"
MIN_INTERVAL_SECONDS = 0.5


class OpenMeteoClient:
    def __init__(self, mode: str = "replay"):
        self.session = FixtureRecordingSession("open_meteo", mode=mode)
        self.limiter = RateLimiter(MIN_INTERVAL_SECONDS)

    def forecast(self, lat: float, lon: float, start_date: date, end_date: date) -> dict:
        self.limiter.wait()
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "temperature_unit": "fahrenheit",
            "precipitation_unit": "inch",
            "timezone": "auto",
        }
        return self.session.get_json(
            BASE_URL, name=f"forecast_{lat}_{lon}_{start_date}_{end_date}", params=params
        )
