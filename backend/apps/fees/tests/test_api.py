"""POST /api/fees/calculate contract."""


def test_calculate_returns_breakdown(api_client):
    payload = {
        "parks": [
            {"slug": "yell", "name": "Yellowstone", "standard_fee": "35.00", "fee_type": "vehicle"},
            {"slug": "grte", "name": "Grand Teton", "standard_fee": "35.00", "fee_type": "vehicle"},
            {"slug": "yose", "name": "Yosemite", "standard_fee": "35.00", "fee_type": "vehicle"},
        ],
        "adults": 2,
        "children": 0,
        "is_us_resident": False,
    }

    response = api_client.post("/api/fees/calculate", payload, format="json")

    assert response.status_code == 200
    assert response.data["annual_pass_total"] == "500.00"
    assert response.data["recommendation"]["cheaper"] == "annual_pass"


def test_calculate_rejects_missing_fields(api_client):
    response = api_client.post("/api/fees/calculate", {"adults": 2}, format="json")

    assert response.status_code == 400


def test_calculate_defaults_children_to_zero(api_client):
    payload = {
        "parks": [{"slug": "zion", "name": "Zion", "standard_fee": "35.00"}],
        "adults": 1,
        "is_us_resident": True,
    }

    response = api_client.post("/api/fees/calculate", payload, format="json")

    assert response.status_code == 200
