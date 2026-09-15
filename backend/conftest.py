import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def spot_factory(db):
    from apps.catalog.tests.factories import SpotFactory

    return SpotFactory
