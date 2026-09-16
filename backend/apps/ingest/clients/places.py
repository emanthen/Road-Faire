"""Google Places — cache 30 days, never on request path.

"Cache 30 days" is the places-monthly Celery beat schedule itself (config/celery.py) —
this client is only ever called from that task, never from a request handler, so a spot
page can never trigger a live (paid) Places call.
"""

from django.conf import settings

from apps.ingest.clients.base import FixtureRecordingSession, RateLimiter

FIND_PLACE_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
MIN_INTERVAL_SECONDS = 0.2


class PlacesClient:
    def __init__(self, mode: str = "replay"):
        self.session = FixtureRecordingSession("places", mode=mode)
        self.limiter = RateLimiter(MIN_INTERVAL_SECONDS)
        self.api_key = getattr(settings, "GOOGLE_PLACES_API_KEY", "")

    def find_place(self, query: str) -> dict:
        """Text search -> the best-matching candidate's place_id for `query`
        (e.g. "Grand Teton National Park visitor center")."""
        self.limiter.wait()
        params = {
            "input": query,
            "inputtype": "textquery",
            "fields": "place_id",
            "key": self.api_key,
        }
        return self.session.get_json(
            FIND_PLACE_URL, name=f"find_{_fixture_name(query)}", params=params
        )

    def details(self, place_id: str, fields: str = "formatted_phone_number") -> dict:
        self.limiter.wait()
        params = {"place_id": place_id, "fields": fields, "key": self.api_key}
        return self.session.get_json(DETAILS_URL, name=f"details_{place_id}", params=params)


def _fixture_name(query: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in query.lower())
