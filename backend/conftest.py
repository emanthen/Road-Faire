import pytest
from django.core.cache import cache
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def _clear_cache():
    """DRF throttling stores hit history in Django's cache, which is one shared
    LocMemCache instance for the whole pytest session — without this, a test that
    trips a scoped rate limit (or just makes enough real requests) eats into whatever
    quota an unrelated, later test needs from the same endpoint."""
    cache.clear()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def spot_factory(db):
    from apps.catalog.tests.factories import SpotFactory

    return SpotFactory
