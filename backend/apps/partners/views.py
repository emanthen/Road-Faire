"""/go/<uuid> -> record Click -> 302. /api/partners/ -> read-only vendor listing."""

from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from apps.catalog.models import Spot
from apps.partners.links import build_url
from apps.partners.models import Click, Offer, Partner
from apps.partners.serializers import PartnerSerializer


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

    utm = {k: v for k, v in request.GET.items() if k.startswith("utm_")}
    referrer = request.META.get("HTTP_REFERER", "")

    Click.objects.create(
        offer=offer,
        spot=spot,
        session_key=request.session.session_key or "",
        referrer=referrer,
        utm=utm,
    )

    url = build_url(
        offer,
        spot_slug=spot_slug,
        session_key=request.session.session_key or "",
        referrer=referrer,
        utm=utm,
    )
    return HttpResponseRedirect(url)
