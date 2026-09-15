"""build_url() tracking param construction."""

import uuid

from apps.partners.links import build_url
from apps.partners.models import Offer, Partner


def _offer(**overrides) -> Offer:
    defaults = dict(
        id=uuid.uuid4(),
        partner=Partner(name="Outdoorsy", slug="outdoorsy"),
        category=Offer.Category.CAMPERVAN,
        base_url="https://example.com/book",
        tracking_params={"aff_id": "roadfare"},
        commission_note="flat $60/booking",
    )
    defaults.update(overrides)
    return Offer(**defaults)


def test_appends_tracking_params_from_offer():
    url = build_url(_offer(), spot_slug=None, session_key="")
    assert "aff_id=roadfare" in url


def test_includes_spot_slug_when_given():
    url = build_url(_offer(), spot_slug="yell", session_key="abc123")
    assert "spot=yell" in url
    assert "session=abc123" in url


def test_omits_spot_and_session_when_not_given():
    url = build_url(_offer(), spot_slug=None, session_key="")
    assert "spot=" not in url
    assert "session=" not in url


def test_includes_utm_params():
    url = build_url(_offer(), utm={"utm_source": "roadfare", "utm_medium": "spot_page"})
    assert "utm_source=roadfare" in url
    assert "utm_medium=spot_page" in url


def test_preserves_existing_query_params_on_base_url():
    offer = _offer(base_url="https://example.com/book?ref=partner")
    url = build_url(offer, spot_slug="zion")
    assert "ref=partner" in url
    assert "spot=zion" in url
