"""/api/health, /api/version — the Phase 1 gate endpoints."""

from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response

API_VERSION = "0.1.0"


@api_view(["GET"])
def health(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    return Response({"status": "ok"})


@api_view(["GET"])
def version(request):
    return Response({"version": API_VERSION})
