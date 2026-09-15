"""seed_demo_guides management command."""

import pytest
from django.core.management import call_command

from apps.content.models import Page

pytestmark = pytest.mark.django_db


def test_seed_creates_three_published_pages():
    call_command("seed_demo_guides")

    assert Page.objects.count() == 3
    assert all(Page.objects.values_list("published", flat=True))


def test_seed_is_idempotent():
    call_command("seed_demo_guides")
    call_command("seed_demo_guides")

    assert Page.objects.count() == 3


def test_seeded_pages_are_served_by_the_content_api(api_client):
    call_command("seed_demo_guides")

    response = api_client.get("/api/content/pages/")

    assert response.status_code == 200
    slugs = {row["slug"] for row in response.data["results"]}
    assert "non-resident-surcharge-explained" in slugs
