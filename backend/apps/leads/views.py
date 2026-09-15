"""POST /api/leads (honeypot + rate limit)."""

from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.leads.models import Lead
from apps.leads.serializers import LeadSerializer


@api_view(["POST"])
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


create_lead.cls.throttle_scope = "leads"
