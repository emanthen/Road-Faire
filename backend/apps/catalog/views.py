"""Read-only spot list/detail, filters, geo bbox search."""

from django.contrib.gis.geos import Polygon
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.catalog.filters import SpotFilter
from apps.catalog.models import Spot
from apps.catalog.serializers import SpotDetailSerializer, SpotListSerializer


class SpotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Spot.objects.select_related("state", "cost").all()
    lookup_field = "slug"
    filterset_class = SpotFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "reservation_rules", "vehicle_limits", "climate_normals", "crowd_indexes",
                "activities", "amenities",
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return SpotListSerializer
        return SpotDetailSerializer

    @action(detail=False)
    def bbox(self, request):
        """?bbox=west,south,east,north — spots whose geom falls within the box."""
        raw = request.query_params.get("bbox", "")
        try:
            west, south, east, north = (float(v) for v in raw.split(","))
        except ValueError:
            detail = "bbox must be 'west,south,east,north'"
            return Response({"error": {"detail": detail}}, status=400)
        box = Polygon.from_bbox((west, south, east, north))
        spots = self.get_queryset().filter(geom__within=box)
        return Response(SpotListSerializer(spots, many=True).data)
