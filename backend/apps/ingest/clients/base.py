"""Rate limit, retry, ETag caching, fixture recording — shared by every ingest client."""

import json
import time
from pathlib import Path

from apps.core.http import get_session


class FixtureRecordingSession:
    """Wraps a requests.Session so tests can run against recorded JSON instead of the
    live API. In "record" mode, every GET response body is saved under
    apps/ingest/fixtures/<source>/<name>.json; in replay mode (the default for tests)
    responses are read from there and no network call is made.
    """

    def __init__(self, source: str, mode: str = "replay"):
        self.source = source
        self.mode = mode
        self.fixtures_dir = Path(__file__).parent.parent / "fixtures" / source
        # Created either way — building a Session doesn't make a network call, and
        # keeping this non-Optional avoids threading None-checks through every method.
        self._session = get_session()

    def get_json(self, url: str, name: str, **kwargs) -> dict:
        fixture_path = self.fixtures_dir / f"{name}.json"
        if self.mode == "replay":
            return json.loads(fixture_path.read_text(encoding="utf-8"))

        response = self._session.get(url, **kwargs)
        response.raise_for_status()
        data = response.json()
        self.fixtures_dir.mkdir(parents=True, exist_ok=True)
        fixture_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data

    def post_json(self, url: str, name: str, **kwargs) -> dict:
        """Same record/replay behavior as get_json, for APIs that require POST (e.g.
        Google Routes' computeRoutes, which has no GET form)."""
        fixture_path = self.fixtures_dir / f"{name}.json"
        if self.mode == "replay":
            return json.loads(fixture_path.read_text(encoding="utf-8"))

        response = self._session.post(url, **kwargs)
        response.raise_for_status()
        data = response.json()
        self.fixtures_dir.mkdir(parents=True, exist_ok=True)
        fixture_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data

    def get_text(self, url: str, name: str, **kwargs) -> str:
        """Same record/replay behavior as get_json, for non-JSON responses (e.g. NOAA's
        CSV normals product)."""
        fixture_path = self.fixtures_dir / f"{name}.csv"
        if self.mode == "replay":
            return fixture_path.read_text(encoding="utf-8")

        response = self._session.get(url, **kwargs)
        response.raise_for_status()
        self.fixtures_dir.mkdir(parents=True, exist_ok=True)
        fixture_path.write_text(response.text, encoding="utf-8")
        return response.text


class RateLimiter:
    """A minimal fixed-interval limiter — enough for the low request volumes ingest
    connectors make (a few dozen calls per run), not a general-purpose token bucket."""

    def __init__(self, min_interval_seconds: float):
        self.min_interval_seconds = min_interval_seconds
        self._last_call: float = 0.0

    def wait(self) -> None:
        elapsed = time.monotonic() - self._last_call
        remaining = self.min_interval_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)
        self._last_call = time.monotonic()
