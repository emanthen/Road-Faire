"""current_fuel_price_per_gallon — weekly cache, last-known fallback, bootstrap floor."""

from decimal import Decimal
from unittest.mock import patch

from django.core.cache import cache

from apps.planner.fuel import BOOTSTRAP_FUEL_PRICE, current_fuel_price_per_gallon


def setup_function():
    cache.clear()


def test_no_key_and_no_prior_fetch_falls_back_to_the_bootstrap_constant():
    with patch("apps.planner.fuel.settings.EIA_API_KEY", ""):
        price, is_estimate = current_fuel_price_per_gallon()

    assert price == BOOTSTRAP_FUEL_PRICE
    assert is_estimate is True


def test_successful_fetch_is_not_flagged_as_an_estimate_and_gets_cached():
    with (
        patch("apps.planner.fuel.settings.EIA_API_KEY", "test-key"),
        patch("apps.planner.fuel._fetch_live", return_value=Decimal("4.25")),
    ):
        price, is_estimate = current_fuel_price_per_gallon()

    assert price == Decimal("4.25")
    assert is_estimate is False


def test_cached_weekly_value_is_reused_without_refetching():
    with (
        patch("apps.planner.fuel.settings.EIA_API_KEY", "test-key"),
        patch("apps.planner.fuel._fetch_live", return_value=Decimal("4.25")) as mock_fetch,
    ):
        current_fuel_price_per_gallon()
        price, is_estimate = current_fuel_price_per_gallon()

    mock_fetch.assert_called_once()
    assert price == Decimal("4.25")
    assert is_estimate is False


def test_fetch_failure_falls_back_to_last_known_value_flagged_as_estimate():
    with (
        patch("apps.planner.fuel.settings.EIA_API_KEY", "test-key"),
        patch("apps.planner.fuel._fetch_live", return_value=Decimal("4.25")),
    ):
        current_fuel_price_per_gallon()  # populates the last-known cache

    cache.delete("eia_fuel_price_weekly")  # simulate the weekly cache expiring

    with (
        patch("apps.planner.fuel.settings.EIA_API_KEY", "test-key"),
        patch("apps.planner.fuel._fetch_live", side_effect=ConnectionError("down")),
    ):
        price, is_estimate = current_fuel_price_per_gallon()

    assert price == Decimal("4.25")
    assert is_estimate is True


def test_fetch_failure_with_no_last_known_value_falls_back_to_bootstrap():
    with (
        patch("apps.planner.fuel.settings.EIA_API_KEY", "test-key"),
        patch("apps.planner.fuel._fetch_live", side_effect=ConnectionError("down")),
    ):
        price, is_estimate = current_fuel_price_per_gallon()

    assert price == BOOTSTRAP_FUEL_PRICE
    assert is_estimate is True
