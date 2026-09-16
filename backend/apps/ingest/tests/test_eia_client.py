"""EIAClient — replays the recorded fixture, no live network call."""

from apps.ingest.clients.eia import DEFAULT_SERIES_ID, EIAClient


def test_weekly_regular_gasoline_price_replays_fixture():
    client = EIAClient(mode="replay")

    response = client.weekly_regular_gasoline_price()

    assert response["response"]["data"][0]["series"] == DEFAULT_SERIES_ID
