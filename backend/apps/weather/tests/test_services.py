"""forecast_for() / normals_for() behavior."""

from datetime import date

import pytest
from django.core.cache import cache

from apps.catalog.tests.factories import ClimateNormalFactory, SpotFactory
from apps.weather.services import forecast_for, normals_for

pytestmark = pytest.mark.django_db


def test_forecast_for_parses_fixture_into_daily_list():
    cache.clear()
    spot = SpotFactory()  # default geom matches the recorded fixture's lat/lon

    result = forecast_for(spot, date(2026, 7, 1), date(2026, 7, 7))

    assert len(result) == 7
    assert result[0] == {"date": "2026-07-01", "high_f": 78.1, "low_f": 45.2, "precip_in": 0.0}


def test_forecast_for_caches_for_one_hour(monkeypatch):
    cache.clear()
    spot = SpotFactory()
    calls = []
    from apps.weather import clients as clients_module

    original_forecast = clients_module.OpenMeteoClient.forecast

    def counting_forecast(self, *args, **kwargs):
        calls.append(1)
        return original_forecast(self, *args, **kwargs)

    monkeypatch.setattr(clients_module.OpenMeteoClient, "forecast", counting_forecast)

    forecast_for(spot, date(2026, 7, 1), date(2026, 7, 7))
    forecast_for(spot, date(2026, 7, 1), date(2026, 7, 7))

    assert len(calls) == 1  # second call hit the cache, not the client


def test_normals_for_reads_catalog_climate_normals_no_external_call():
    spot = SpotFactory()
    ClimateNormalFactory(spot=spot, month=7, high_f="80.0", low_f="50.0", precip_in="1.0")

    result = normals_for(spot)

    assert result == [{"month": 7, "high_f": 80.0, "low_f": 50.0, "precip_in": 1.0}]
