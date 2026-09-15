"""ScopedRateThrottle on POST /api/leads (scope "leads").

See apps/fees/tests/test_throttle.py for why this patches THROTTLE_RATES directly
instead of using override_settings.
"""

import pytest
from django.core.cache import cache
from rest_framework.throttling import SimpleRateThrottle

pytestmark = pytest.mark.django_db


def test_create_lead_returns_429_past_its_scoped_limit(api_client, monkeypatch):
    monkeypatch.setitem(SimpleRateThrottle.THROTTLE_RATES, "leads", "2/min")
    cache.clear()

    for _ in range(2):
        response = api_client.post("/api/leads/", {}, format="json")
        assert response.status_code != 429

    response = api_client.post("/api/leads/", {}, format="json")

    assert response.status_code == 429
