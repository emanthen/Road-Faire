"""leg_waypoints against a mocked Overpass response — no live network call."""

from unittest.mock import patch

from django.core.cache import cache

from apps.planner.engine.waypoints import LegWaypoints, leg_waypoints

FUEL_ELEMENTS = {
    "elements": [
        {"type": "node", "lat": 44.50, "lon": -110.60, "tags": {"name": "Near Pump"}},
        {"type": "node", "lat": 45.00, "lon": -111.00, "tags": {"name": "Far Pump"}},
    ]
}
EMPTY = {"elements": []}


def setup_function():
    cache.clear()


def test_leg_waypoints_picks_the_nearest_node():
    with patch(
        "apps.planner.engine.waypoints._query", side_effect=[FUEL_ELEMENTS, EMPTY]
    ):
        result = leg_waypoints(44.428, -110.5885, 44.60, -110.70)

    assert isinstance(result, LegWaypoints)
    assert result.fuel is not None
    assert result.fuel.name == "Near Pump"
    assert result.restaurant is None


def test_leg_waypoints_is_cached_and_does_not_re_query():
    with patch(
        "apps.planner.engine.waypoints._query", side_effect=[EMPTY, EMPTY]
    ) as mock_query:
        leg_waypoints(40.0, -100.0, 40.1, -100.1)
        leg_waypoints(40.0, -100.0, 40.1, -100.1)

    assert mock_query.call_count == 2  # only the first call hit Overpass


def test_leg_waypoints_returns_none_fields_when_overpass_is_unreachable():
    with patch("apps.planner.engine.waypoints._query", side_effect=ConnectionError):
        result = leg_waypoints(1.0, 1.0, 2.0, 2.0)

    assert result == LegWaypoints(fuel=None, restaurant=None)
