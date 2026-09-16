"""EIA weekly regional gasoline price (api.eia.gov) — free key, BUILD_PROMPT §3.

Fixture-recordable like every other apps.ingest client. Caching/fallback to the last
successfully fetched value lives in apps.planner.fuel, not here — this client is just
the raw API wrapper.
"""

from django.conf import settings

from apps.ingest.clients.base import FixtureRecordingSession, RateLimiter

BASE_URL = "https://api.eia.gov/v2/petroleum/pri/gnd/data/"
MIN_INTERVAL_SECONDS = 0.5

# PADD (Petroleum Administration for Defense District) regional series — "R10" is the
# US average; a specific PADD (e.g. "R30" = Midwest) could be resolved from a trip's
# region later, same way apps.planner.rates resolves state-level lodging ranges.
DEFAULT_SERIES_ID = "EMM_EPMR_PTE_NUS_DPG"  # US Regular All Formulations, weekly, $/gal


class EIAClient:
    def __init__(self, mode: str = "replay"):
        self.session = FixtureRecordingSession("eia", mode=mode)
        self.limiter = RateLimiter(MIN_INTERVAL_SECONDS)
        self.api_key = getattr(settings, "EIA_API_KEY", "")

    def weekly_regular_gasoline_price(self, series_id: str = DEFAULT_SERIES_ID) -> dict:
        """Raw API response — most recent weekly observations for `series_id`.
        apps.planner.fuel extracts and caches the single most recent price."""
        self.limiter.wait()
        params = {
            "api_key": self.api_key,
            "frequency": "weekly",
            "data[0]": "value",
            "facets[series][]": series_id,
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "length": 1,
        }
        return self.session.get_json(BASE_URL, name=f"weekly_{series_id}", params=params)
