"""PlacesClient — replays recorded fixtures, no live network call."""

from apps.ingest.clients.places import PlacesClient


def test_find_place_replays_fixture():
    client = PlacesClient(mode="replay")

    response = client.find_place("Test Park visitor center")

    assert response["candidates"][0]["place_id"] == "ChIJ_test_place_id"


def test_details_replays_fixture():
    client = PlacesClient(mode="replay")

    response = client.details("ChIJ_test_place_id")

    assert response["result"]["formatted_phone_number"] == "(307) 555-0100"
