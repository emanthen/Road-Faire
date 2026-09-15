"""1991-2020 climate normals bulk loader.

Pulls per-station monthly normals from NOAA NCEI's public 1991-2020 Normals bulk-access
product (no API key required). One station per call — the ingest command calls this once
per seed spot's nearest station, not a full continental bulk download.
"""

import csv
import io

from apps.ingest.clients.base import FixtureRecordingSession, RateLimiter

BASE_URL = "https://www.ncei.noaa.gov/pub/data/normals/1991-2020/access"
MIN_INTERVAL_SECONDS = 0.5

# Column prefixes in the per-station CSV for the fields ClimateNormal needs.
_MONTHLY_COLUMNS = {
    "high_f": "MLY-TMAX-NORMAL",
    "low_f": "MLY-TMIN-NORMAL",
    "precip_in": "MLY-PRCP-NORMAL",
    "snow_in": "MLY-SNOW-NORMAL",
}


class NOAAClient:
    def __init__(self, mode: str = "replay"):
        self.session = FixtureRecordingSession("noaa", mode=mode)
        self.limiter = RateLimiter(MIN_INTERVAL_SECONDS)

    def monthly_normals(self, station_id: str) -> list[dict]:
        """Returns one dict per month (1-12) with high_f/low_f/precip_in/snow_in."""
        self.limiter.wait()
        url = f"{BASE_URL}/{station_id}.csv"
        raw = self.session.get_text(url, name=f"station_{station_id}")
        return self._parse(raw)

    @staticmethod
    def _parse(raw_csv: str) -> list[dict]:
        reader = csv.DictReader(io.StringIO(raw_csv))
        rows = list(reader)
        if not rows:
            return []
        row = rows[0]  # NOAA's per-station file is a single row of named monthly columns
        months = []
        for month in range(1, 13):
            months.append(
                {
                    "month": month,
                    **{
                        field: row.get(f"{prefix}{month:02d}", "")
                        for field, prefix in _MONTHLY_COLUMNS.items()
                    },
                }
            )
        return months
