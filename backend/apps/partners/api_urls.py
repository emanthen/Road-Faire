from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.partners.views import PartnerViewSet

router = DefaultRouter()
router.register("", PartnerViewSet, basename="partner")

urlpatterns = [
    path("", include(router.urls)),
]
