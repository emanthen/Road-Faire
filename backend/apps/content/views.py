from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.content.models import FAQ, Page, SiteSettings
from apps.content.serializers import FAQSerializer, PageSerializer, SiteSettingsSerializer
from apps.content.sitemap import sitemap_entries


class PageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.filter(published=True)
    serializer_class = PageSerializer
    lookup_field = "slug"


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer


@api_view(["GET"])
def sitemap(request):
    return Response(sitemap_entries())


@api_view(["GET"])
def site_settings(request):
    # first() rather than get(): a fresh install has no row yet, and the singleton is
    # enforced in admin.py, not the DB — never 500 the whole site over branding.
    settings_row = SiteSettings.objects.first() or SiteSettings()
    return Response(SiteSettingsSerializer(settings_row).data)
