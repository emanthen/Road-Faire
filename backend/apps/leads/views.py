"""POST /api/leads (honeypot + rate limit)."""

from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from apps.leads.models import Lead
from apps.leads.serializers import LeadSerializer


class LeadRateThrottle(AnonRateThrottle):
    rate = "5/hour"


@api_view(["POST"])
@throttle_classes([LeadRateThrottle])
def create_lead(request):
    serializer = LeadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    # Honeypot check happens before any DB access: a bot filling in `website` gets a
    # fake success response and never touches the database, so it has no signal that
    # it was caught. This branch is real, testable logic — no `db` fixture needed.
    if data["website"]:
        return Response({"status": "ok"}, status=201)

    Lead.objects.create(email=data["email"], source=data["source"])
    return Response({"status": "ok"}, status=201)
