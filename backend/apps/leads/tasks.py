"""Resend send, welcome sequence.

Wraps the Resend HTTP API — real function shape, but not exercisable without
RESEND_API_KEY (blank in .env). No mode="record"/"replay" fixture split here like
apps.ingest's clients: Resend is a send-only API (there's nothing to replay — sending
twice sends two real emails), so this stays untested until there's a real key and a
sandbox/test-mode address to send to.
"""

from celery import shared_task
from django.conf import settings

from apps.core.http import get_session
from apps.leads.models import EmailEvent, Lead

RESEND_API_URL = "https://api.resend.com/emails"
FROM_ADDRESS = "Roadfare <hello@roadfare.com>"


@shared_task
def send_welcome_email(lead_id: int) -> None:
    lead = Lead.objects.get(id=lead_id)
    api_key = getattr(settings, "RESEND_API_KEY", "")
    if not api_key:
        raise RuntimeError("RESEND_API_KEY is not set — cannot send email.")

    session = get_session()
    session.post(
        RESEND_API_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "from": FROM_ADDRESS,
            "to": [lead.email],
            "subject": "Welcome to Roadfare",
            "html": "<p>Thanks for signing up — we'll be in touch with trip ideas.</p>",
        },
    )
    EmailEvent.objects.create(lead=lead, event_type=EmailEvent.EventType.WELCOME_SENT)
