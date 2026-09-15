"""build_url(offer, spot, session) with tracking params."""

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from apps.partners.models import Offer


def build_url(
    offer: Offer,
    spot_slug: str | None = None,
    session_key: str = "",
    referrer: str = "",
    utm: dict | None = None,
) -> str:
    """Appends offer.tracking_params plus spot/session/utm onto offer.base_url. Pure —
    takes an Offer instance's field values, doesn't require it to be saved."""
    parsed = urlparse(offer.base_url)
    params = dict(parse_qsl(parsed.query))

    params.update(offer.tracking_params or {})
    if spot_slug:
        params["spot"] = spot_slug
    if session_key:
        params["session"] = session_key
    if referrer:
        params["referrer"] = referrer
    if utm:
        params.update(utm)

    return urlunparse(parsed._replace(query=urlencode(params)))
