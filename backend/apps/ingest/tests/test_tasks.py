"""eia_fuel_weekly — pre-warms apps.planner.fuel's cache."""

from unittest.mock import patch

from apps.ingest.tasks import eia_fuel_weekly


def test_calls_current_fuel_price_per_gallon():
    with patch("apps.planner.fuel.current_fuel_price_per_gallon") as mock_fn:
        eia_fuel_weekly()

    mock_fn.assert_called_once()
