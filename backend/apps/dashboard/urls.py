from rest_framework.routers import DefaultRouter

from apps.dashboard.views import (
    FAQAdminViewSet,
    OfferAdminViewSet,
    PageAdminViewSet,
    PartnerAdminViewSet,
    PhotoAdminViewSet,
    ReservationRuleAdminViewSet,
    SiteSettingsAdminViewSet,
    SpotAdminViewSet,
    SpotCostAdminViewSet,
    StateAdminViewSet,
    VehicleLimitAdminViewSet,
)

router = DefaultRouter()
router.register("states", StateAdminViewSet, basename="admin-state")
router.register("spots", SpotAdminViewSet, basename="admin-spot")
router.register("spot-costs", SpotCostAdminViewSet, basename="admin-spot-cost")
router.register("reservation-rules", ReservationRuleAdminViewSet, basename="admin-reservation-rule")
router.register("vehicle-limits", VehicleLimitAdminViewSet, basename="admin-vehicle-limit")
router.register("photos", PhotoAdminViewSet, basename="admin-photo")
router.register("partners", PartnerAdminViewSet, basename="admin-partner")
router.register("offers", OfferAdminViewSet, basename="admin-offer")
router.register("pages", PageAdminViewSet, basename="admin-page")
router.register("faqs", FAQAdminViewSet, basename="admin-faq")
router.register("site-settings", SiteSettingsAdminViewSet, basename="admin-site-settings")

urlpatterns = router.urls
