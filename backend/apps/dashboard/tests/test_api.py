"""Staff-only access + basic CRUD for the /api/admin/ dashboard API."""

import pytest

from apps.catalog.tests.factories import SpotCostFactory, SpotFactory, StateFactory
from apps.content.models import Page
from apps.partners.models import Partner

pytestmark = pytest.mark.django_db


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", password="pw", is_staff=True
    )


@pytest.fixture
def regular_user(django_user_model):
    return django_user_model.objects.create_user(username="regular", password="pw")


def test_anonymous_cannot_list_spots(api_client):
    response = api_client.get("/api/admin/spots/")

    # TokenAuthentication is among the global DEFAULT_AUTHENTICATION_CLASSES, so DRF
    # reports an anonymous rejection as 401 (not authenticated) rather than 403.
    assert response.status_code == 401


def test_non_staff_cannot_list_spots(api_client, regular_user):
    api_client.force_authenticate(user=regular_user)

    response = api_client.get("/api/admin/spots/")

    assert response.status_code == 403


def test_staff_can_list_spots(api_client, staff_user):
    SpotFactory(name="Admin-visible Spot")
    api_client.force_authenticate(user=staff_user)

    response = api_client.get("/api/admin/spots/")

    assert response.status_code == 200
    names = {row["name"] for row in response.data["results"]}
    assert "Admin-visible Spot" in names


def test_staff_can_create_update_delete_spot(api_client, staff_user):
    state = StateFactory()
    api_client.force_authenticate(user=staff_user)

    create_response = api_client.post(
        "/api/admin/spots/",
        {
            "name": "New Spot",
            "slug": "new-spot",
            "state": state.id,
            "type": "national_park",
            "min_days": 2,
            "latitude": 44.0,
            "longitude": -110.0,
        },
        format="json",
    )
    assert create_response.status_code == 201
    slug = create_response.data["slug"]

    update_response = api_client.patch(
        f"/api/admin/spots/{slug}/", {"name": "Renamed Spot"}, format="json"
    )
    assert update_response.status_code == 200
    assert update_response.data["name"] == "Renamed Spot"

    delete_response = api_client.delete(f"/api/admin/spots/{slug}/")
    assert delete_response.status_code == 204


def test_staff_can_create_update_delete_page(api_client, staff_user):
    api_client.force_authenticate(user=staff_user)

    create_response = api_client.post(
        "/api/admin/pages/",
        {
            "title": "New Article",
            "slug": "new-article",
            "body": "Body text.",
            "published": False,
            "meta_title": "New Article | Roadfare",
            "meta_description": "A test article.",
        },
        format="json",
    )
    assert create_response.status_code == 201
    assert Page.objects.filter(slug="new-article").exists()

    update_response = api_client.patch(
        "/api/admin/pages/new-article/", {"published": True}, format="json"
    )
    assert update_response.status_code == 200
    assert update_response.data["published"] is True

    delete_response = api_client.delete("/api/admin/pages/new-article/")
    assert delete_response.status_code == 204
    assert not Page.objects.filter(slug="new-article").exists()


# These four resources have no `created_at` field (VerifiableModel/plain Model, not
# TimeStampedModel), so their viewsets set pagination_class = None — the global
# DefaultCursorPagination orders by "-created_at" and would 500 on every one of them
# otherwise. Each test below lists the endpoint to prove that fix actually holds.


def test_staff_can_list_partners_unpaginated(api_client, staff_user):
    Partner.objects.create(name="Acme Rentals", slug="acme-rentals")
    api_client.force_authenticate(user=staff_user)

    response = api_client.get("/api/admin/partners/")

    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert any(row["slug"] == "acme-rentals" for row in response.data)


def test_staff_can_list_faqs_unpaginated(api_client, staff_user):
    api_client.force_authenticate(user=staff_user)

    create_response = api_client.post(
        "/api/admin/faqs/", {"question": "Is it free?", "answer": "No.", "order": 1},
        format="json",
    )
    assert create_response.status_code == 201

    list_response = api_client.get("/api/admin/faqs/")
    assert list_response.status_code == 200
    assert isinstance(list_response.data, list)


def test_staff_can_list_site_settings_unpaginated(api_client, staff_user):
    api_client.force_authenticate(user=staff_user)

    response = api_client.get("/api/admin/site-settings/")

    assert response.status_code == 200
    assert isinstance(response.data, list)


def test_staff_can_list_spot_costs_scoped_to_spot(api_client, staff_user):
    cost = SpotCostFactory()
    api_client.force_authenticate(user=staff_user)

    response = api_client.get(f"/api/admin/spot-costs/?spot={cost.spot_id}")

    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert response.data[0]["spot"] == cost.spot_id
