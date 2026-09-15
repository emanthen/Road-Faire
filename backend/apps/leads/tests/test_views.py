"""POST /api/leads honeypot behavior — the only branch testable without the db fixture:
a triggered honeypot returns success without ever touching the database.

Neither test below requests the `db` fixture. pytest-django blocks any actual database
access in that case (raises RuntimeError rather than silently allowing it), so the first
test passing at all is itself proof the honeypot branch never reached Lead.objects.create().
"""


def test_honeypot_triggered_returns_success_without_creating_lead(api_client):
    response = api_client.post(
        "/api/leads/",
        {"email": "bot@example.com", "source": "homepage", "website": "https://spam.example"},
        format="json",
    )

    assert response.status_code == 201
    assert response.data == {"status": "ok"}


def test_missing_email_is_rejected(api_client):
    response = api_client.post(
        "/api/leads/", {"source": "homepage", "website": ""}, format="json"
    )

    assert response.status_code == 400
