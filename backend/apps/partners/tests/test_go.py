"""/go/<uuid> — dedupe window and bot flagging (views.go, bots.is_bot_user_agent)."""

import pytest

from apps.partners.bots import is_bot_user_agent
from apps.partners.models import Click, Offer, Partner

pytestmark = pytest.mark.django_db


def _offer() -> Offer:
    partner = Partner.objects.create(name="Outdoorsy", slug="outdoorsy")
    return Offer.objects.create(
        partner=partner,
        category=Offer.Category.CAMPERVAN,
        base_url="https://example.com/book",
    )


def test_redirects_and_records_a_click(api_client):
    offer = _offer()

    response = api_client.get(f"/go/{offer.id}")

    assert response.status_code == 302
    assert Click.objects.filter(offer=offer).count() == 1


def test_repeat_hit_within_dedupe_window_is_not_recorded_twice(api_client):
    offer = _offer()

    api_client.get(f"/go/{offer.id}")
    api_client.get(f"/go/{offer.id}")

    assert Click.objects.filter(offer=offer).count() == 1


def test_bot_user_agent_is_flagged_but_still_recorded(api_client):
    offer = _offer()

    api_client.get(f"/go/{offer.id}", HTTP_USER_AGENT="Mozilla/5.0 (compatible; AhrefsBot/7.0)")

    click = Click.objects.get(offer=offer)
    assert click.is_bot is True


@pytest.mark.parametrize(
    "user_agent,expected",
    [
        ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0 Safari/537.36", False),
        ("curl/8.4.0", True),
        ("python-requests/2.31.0", True),
        ("Googlebot/2.1 (+http://www.google.com/bot.html)", True),
        ("", False),
    ],
)
def test_is_bot_user_agent(user_agent, expected):
    assert is_bot_user_agent(user_agent) is expected
