from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.content.views import FAQViewSet, PageViewSet, site_settings, sitemap

router = DefaultRouter()
router.register("pages", PageViewSet, basename="page")
router.register("faqs", FAQViewSet, basename="faq")

urlpatterns = [
    path("sitemap", sitemap, name="content-sitemap"),
    path("settings", site_settings, name="content-settings"),
    path("", include(router.urls)),
]
