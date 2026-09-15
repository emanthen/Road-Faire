from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.vehicles.views import VehicleSpecViewSet, size_check, true_cost_view

router = DefaultRouter()
router.register("", VehicleSpecViewSet, basename="vehicle-spec")

urlpatterns = [
    path("size-check", size_check, name="vehicles-size-check"),
    path("true-cost", true_cost_view, name="vehicles-true-cost"),
    path("", include(router.urls)),
]
