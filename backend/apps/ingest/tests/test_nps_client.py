"""NPS client against recorded HTTP fixtures."""

from apps.ingest.clients.nps import NPSClient


def test_park_returns_parsed_fixture():
    client = NPSClient(mode="replay")
    payload = client.park("TEST")
    assert payload["data"][0]["fullName"] == "Test National Park"


def test_fees_returns_entrance_fees():
    client = NPSClient(mode="replay")
    payload = client.fees("TEST")
    fees = payload["data"][0]["entranceFees"]
    assert any(f["title"] == "Vehicle" and f["cost"] == "35.00" for f in fees)


def test_alerts_returns_empty_list_when_none():
    client = NPSClient(mode="replay")
    payload = client.alerts("TEST")
    assert payload["data"] == []
