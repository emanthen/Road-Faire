"""current_fuel_price_per_gallon() — EIA-backed with a persistent last-known fallback.

BUILD_PROMPT C2: "cache weekly... fall back to the last stored value, never to a
hardcoded number." Two cache keys: a weekly one that says "this is fresh, don't refetch
yet", and a no-expiry one that's the actual fallback — updated whenever a fetch
succeeds, read whenever one doesn't. Only when NEITHER has ever been populated (a fresh
install with no EIA_API_KEY configured yet) does this fall back to a hardcoded
cost-model assumption — same status as apps.planner.engine.costing's other bootstrap
constants, and always flagged is_estimate in that case.
"""

import logging
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache

from apps.ingest.clients.eia import EIAClient

logger = logging.getLogger(__name__)

_WEEKLY_CACHE_KEY = "eia_fuel_price_weekly"
_LAST_KNOWN_CACHE_KEY = "eia_fuel_price_last_known"
_WEEKLY_TTL_SECONDS = 7 * 24 * 60 * 60

# Bootstrap fallback — a cost-model assumption, not a cited fact, same status as the
# planner's other flat constants. Used only when no EIA value has ever been fetched.
BOOTSTRAP_FUEL_PRICE = Decimal("3.80")


def current_fuel_price_per_gallon() -> tuple[Decimal, bool]:
    """Returns (price, is_estimate). is_estimate is False only for a price fetched
    from EIA within the last 7 days — a stale last-known value or the bootstrap
    constant both count as an estimate, even though the former is real cited data,
    because neither is confirmed current."""

    cached = cache.get(_WEEKLY_CACHE_KEY)
    if cached is not None:
        return Decimal(cached), False

    if settings.EIA_API_KEY:
        try:
            price = _fetch_live()
        except Exception:
            logger.warning("EIA fuel price fetch failed; falling back", exc_info=True)
        else:
            cache.set(_WEEKLY_CACHE_KEY, str(price), timeout=_WEEKLY_TTL_SECONDS)
            cache.set(_LAST_KNOWN_CACHE_KEY, str(price), timeout=None)
            return price, False

    last_known = cache.get(_LAST_KNOWN_CACHE_KEY)
    if last_known is not None:
        return Decimal(last_known), True

    return BOOTSTRAP_FUEL_PRICE, True


def _fetch_live() -> Decimal:
    response = EIAClient().weekly_regular_gasoline_price()
    observation = response["response"]["data"][0]
    return Decimal(str(observation["value"]))
