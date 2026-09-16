"""ScopedRateThrottle on /api/fees/calculate (scope "fees").

Patches `SimpleRateThrottle.THROTTLE_RATES` directly rather than using
`override_settings(REST_FRAMEWORK=...)`: DRF binds `THROTTLE_RATES` to
`api_settings.DEFAULT_THROTTLE_RATES` once, in the throttling module's class body, at
first import — override_settings changes django settings and fires DRF's reload signal,
but that signal only resets `api_settings`'s own cache, not this already-bound dict, so
the override never reaches the throttle in a second test in the same process.
"""

import pytest
from django.core.cache import cache
from rest_framework.throttling import SimpleRateThrottle

pytestmark = pytest.mark.django_db


def test_calculate_returns_429_past_its_scoped_limit(api_client, monkeypatch):
    monkeypatch.setitem(SimpleRateThrottle.THROTTLE_RATES, "fees", "2/min")
    cache.clear()

    for _ in range(2):
        response = api_client.post("/api/fees/calculate", {}, format="json")
        assert response.status_code != 429

    response = api_client.post("/api/fees/calculate", {}, format="json")

    assert response.status_code == 429
    cache.clear()  # don't leak this test's throttle hits into whatever runs next
