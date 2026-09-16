"""/go/<uuid> -> record Click -> 302. /api/partners/ -> read-only vendor listing."""

from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets

from apps.catalog.models import Spot
from apps.partners.bots import is_bot_user_agent
from apps.partners.links import build_url
from apps.partners.models import Click, Offer, Partner
from apps.partners.serializers import PartnerSerializer

# The same visitor hitting the same offer again inside this window is a double-fire
# (page reload, back button, a prefetch) rather than a second real referral, so it
# isn't written as a second row — unlike a bot hit, which still gets recorded (see
# Click.is_bot below) because it's real audit trail, just not a real referral either.
DEDUPE_WINDOW = timezone.timedelta(seconds=10)


class PartnerViewSet(viewsets.ReadOnlyModelViewSet):
    """A handful of vendors — no cursor pagination needed (Partner has no created_at)."""

    queryset = Partner.objects.prefetch_related("offers").order_by("name")
    serializer_class = PartnerSerializer
    lookup_field = "slug"
    pagination_class = None


def go(request: HttpRequest, offer_id: str) -> HttpResponseRedirect:
    offer = get_object_or_404(Offer, id=offer_id)
    spot_slug = request.GET.get("spot")
    spot = Spot.objects.filter(slug=spot_slug).first() if spot_slug else None

    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key or ""

    utm = {k: v for k, v in request.GET.items() if k.startswith("utm_")}
    referrer = request.META.get("HTTP_REFERER", "")
    user_agent = request.META.get("HTTP_USER_AGENT", "")

    is_recent_duplicate = Click.objects.filter(
        offer=offer,
        session_key=session_key,
        created_at__gte=timezone.now() - DEDUPE_WINDOW,
    ).exists()

    if not is_recent_duplicate:
        Click.objects.create(
            offer=offer,
            spot=spot,
            session_key=session_key,
            referrer=referrer,
            utm=utm,
            is_bot=is_bot_user_agent(user_agent),
        )

    url = build_url(
        offer,
        spot_slug=spot_slug,
        session_key=session_key,
        referrer=referrer,
        utm=utm,
    )
    return HttpResponseRedirect(url)
