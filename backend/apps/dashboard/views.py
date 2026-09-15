"""Staff-only CRUD viewsets backing the Next.js /dashboard admin UI."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, viewsets

from apps.catalog.models import Photo, ReservationRule, Spot, SpotCost, State, VehicleLimit
from apps.content.models import FAQ, Page, SiteSettings
from apps.core.permissions import IsStaffUser
from apps.dashboard.serializers import (
    FAQAdminSerializer,
    OfferAdminSerializer,
    PageAdminSerializer,
    PartnerAdminSerializer,
    PhotoAdminSerializer,
    ReservationRuleAdminSerializer,
    SiteSettingsAdminSerializer,
    SpotAdminSerializer,
    SpotCostAdminSerializer,
    StateAdminSerializer,
    VehicleLimitAdminSerializer,
)
from apps.partners.models import Offer, Partner


class StaffModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]


class StateAdminViewSet(viewsets.ReadOnlyModelViewSet):
    # No created_at on State (plain Model) — and it's a fixed, small reference list.
    permission_classes = [IsStaffUser]
    queryset = State.objects.select_related("region").all()
    serializer_class = StateAdminSerializer
    pagination_class = None


class SpotAdminViewSet(StaffModelViewSet):
    queryset = Spot.objects.select_related("state").all()
    serializer_class = SpotAdminSerializer
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["state", "type"]
    search_fields = ["name", "slug"]


class SpotCostAdminViewSet(StaffModelViewSet):
    # No cursor pagination: SpotCost has no created_at (VerifiableModel only, not
    # TimeStampedModel), which is what the global DefaultCursorPagination orders by —
    # and every list here is already scoped to one spot via ?spot=, so it's short.
    queryset = SpotCost.objects.all()
    serializer_class = SpotCostAdminSerializer
    filterset_fields = ["spot"]
    pagination_class = None


class ReservationRuleAdminViewSet(StaffModelViewSet):
    queryset = ReservationRule.objects.all()
    serializer_class = ReservationRuleAdminSerializer
    filterset_fields = ["spot"]
    pagination_class = None


class VehicleLimitAdminViewSet(StaffModelViewSet):
    queryset = VehicleLimit.objects.all()
    serializer_class = VehicleLimitAdminSerializer
    filterset_fields = ["spot"]
    pagination_class = None


class PhotoAdminViewSet(StaffModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoAdminSerializer
    filterset_fields = ["spot"]
    pagination_class = None


class PartnerAdminViewSet(StaffModelViewSet):
    # Same reasoning as apps.partners.views.PartnerViewSet: Partner has no created_at
    # either, and it's a handful of vendors — no pagination needed.
    queryset = Partner.objects.all()
    serializer_class = PartnerAdminSerializer
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "slug"]
    pagination_class = None


class OfferAdminViewSet(StaffModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferAdminSerializer
    filterset_fields = ["partner"]


class PageAdminViewSet(StaffModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageAdminSerializer
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "slug"]


class FAQAdminViewSet(StaffModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQAdminSerializer
    pagination_class = None


class SiteSettingsAdminViewSet(StaffModelViewSet):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsAdminSerializer
    pagination_class = None

    def perform_create(self, serializer):
        if SiteSettings.objects.exists():
            raise serializers.ValidationError(
                "Site settings already exist — edit the existing row instead of creating another."
            )
        serializer.save()
