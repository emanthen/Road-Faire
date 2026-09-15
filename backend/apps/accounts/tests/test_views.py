"""POST /api/auth/register, /login, /google, /logout, GET /api/auth/me."""

from unittest.mock import patch

import pytest
from django.contrib.auth.models import User

pytestmark = pytest.mark.django_db


def test_register_creates_a_user_and_returns_a_token(api_client):
    response = api_client.post(
        "/api/auth/register",
        {
            "username": "roadtripper",
            "email": "roadtripper@example.com",
            "password": "correct-horse-battery",
        },
    )

    assert response.status_code == 201
    assert response.data["user"]["username"] == "roadtripper"
    assert response.data["token"]


def test_register_rejects_duplicate_username(api_client):
    api_client.post(
        "/api/auth/register",
        {"username": "roadtripper", "email": "a@example.com", "password": "correct-horse-battery"},
    )
    response = api_client.post(
        "/api/auth/register",
        {"username": "roadtripper", "email": "b@example.com", "password": "correct-horse-battery"},
    )

    assert response.status_code == 400


def test_register_rejects_weak_password(api_client):
    response = api_client.post(
        "/api/auth/register",
        {"username": "roadtripper", "email": "a@example.com", "password": "1234"},
    )

    assert response.status_code == 400


def test_login_returns_a_token_for_correct_credentials(api_client):
    api_client.post(
        "/api/auth/register",
        {"username": "roadtripper", "email": "a@example.com", "password": "correct-horse-battery"},
    )

    response = api_client.post(
        "/api/auth/login", {"username": "roadtripper", "password": "correct-horse-battery"}
    )

    assert response.status_code == 200
    assert response.data["token"]


def test_login_rejects_wrong_password(api_client):
    api_client.post(
        "/api/auth/register",
        {"username": "roadtripper", "email": "a@example.com", "password": "correct-horse-battery"},
    )

    response = api_client.post("/api/auth/login", {"username": "roadtripper", "password": "wrong"})

    assert response.status_code == 400


def test_me_requires_a_token(api_client):
    response = api_client.get("/api/auth/me")

    assert response.status_code == 401


def test_me_returns_the_authenticated_user(api_client):
    register_response = api_client.post(
        "/api/auth/register",
        {"username": "roadtripper", "email": "a@example.com", "password": "correct-horse-battery"},
    )
    token = register_response.data["token"]

    response = api_client.get("/api/auth/me", HTTP_AUTHORIZATION=f"Token {token}")

    assert response.status_code == 200
    assert response.data["username"] == "roadtripper"


def test_google_login_returns_503_when_not_configured(api_client, settings):
    settings.GOOGLE_OAUTH_CLIENT_ID = ""

    response = api_client.post("/api/auth/google", {"id_token": "whatever"})

    assert response.status_code == 503


def test_google_login_creates_a_user_from_a_valid_token(api_client, settings):
    settings.GOOGLE_OAUTH_CLIENT_ID = "test-client-id"

    with patch("apps.accounts.views.google_id_token.verify_oauth2_token") as mock_verify:
        mock_verify.return_value = {"email": "traveler@example.com", "given_name": "Sam"}
        response = api_client.post("/api/auth/google", {"id_token": "a-real-looking-jwt"})

    assert response.status_code == 200
    assert response.data["user"]["email"] == "traveler@example.com"
    assert User.objects.filter(email="traveler@example.com").count() == 1


def test_google_login_reuses_an_existing_user_with_the_same_email(api_client, settings):
    settings.GOOGLE_OAUTH_CLIENT_ID = "test-client-id"
    existing = User.objects.create_user(username="traveler", email="traveler@example.com")

    with patch("apps.accounts.views.google_id_token.verify_oauth2_token") as mock_verify:
        mock_verify.return_value = {"email": "traveler@example.com"}
        response = api_client.post("/api/auth/google", {"id_token": "a-real-looking-jwt"})

    assert response.status_code == 200
    assert response.data["user"]["id"] == existing.id
    assert User.objects.filter(email="traveler@example.com").count() == 1


def test_google_login_rejects_an_invalid_token(api_client, settings):
    settings.GOOGLE_OAUTH_CLIENT_ID = "test-client-id"

    with patch("apps.accounts.views.google_id_token.verify_oauth2_token") as mock_verify:
        mock_verify.side_effect = ValueError("bad token")
        response = api_client.post("/api/auth/google", {"id_token": "not-a-jwt"})

    assert response.status_code == 401


def test_logout_invalidates_the_token(api_client):
    register_response = api_client.post(
        "/api/auth/register",
        {"username": "roadtripper", "email": "a@example.com", "password": "correct-horse-battery"},
    )
    token = register_response.data["token"]

    logout_response = api_client.post("/api/auth/logout", HTTP_AUTHORIZATION=f"Token {token}")
    me_response = api_client.get("/api/auth/me", HTTP_AUTHORIZATION=f"Token {token}")

    assert logout_response.status_code == 204
    assert me_response.status_code == 401
