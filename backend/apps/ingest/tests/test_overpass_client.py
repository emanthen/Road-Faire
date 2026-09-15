"""Overpass client against recorded HTTP fixtures — trails/dump stations/water."""

from apps.ingest.clients.overpass import OverpassClient

LAT, LON = 44.428, -110.5885


def test_trails_near_returns_parsed_fixture():
    client = OverpassClient(mode="replay")
    payload = client.trails_near(LAT, LON)
    assert payload["elements"][0]["tags"]["highway"] == "path"


def test_dump_stations_near_returns_parsed_fixture():
    client = OverpassClient(mode="replay")
    payload = client.dump_stations_near(LAT, LON)
    assert payload["elements"][0]["tags"]["amenity"] == "sanitary_dump_station"


def test_water_near_returns_parsed_fixture():
    client = OverpassClient(mode="replay")
    payload = client.water_near(LAT, LON)
    assert payload["elements"][0]["tags"]["amenity"] == "drinking_water"
