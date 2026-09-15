"""/api/weather/<slug>."""

from datetime import date, timedelta

from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.catalog.models import Spot
from apps.weather.services import forecast_for, normals_for


@api_view(["GET"])
def weather(request, slug: str):
    spot = Spot.objects.get(slug=slug)

    today = date.today()
    forecast = forecast_for(spot, today, today + timedelta(days=6))
    normals = normals_for(spot)

    return Response({"forecast": forecast, "normals": normals})
