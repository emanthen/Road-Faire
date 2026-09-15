"""Celery beat: nps_daily, ridb_daily, places_monthly.

Task bodies just call the management commands so the logic has one home. Not exercised
yet — no Redis-compatible broker running natively (flagged in the Phase 1 gate report);
these will actually fire once Docker (or a native Redis) is set up.
"""

from celery import shared_task
from django.core.management import call_command


@shared_task
def nps_daily():
    call_command("ingest_nps", mode="record")


@shared_task
def ridb_daily():
    call_command("ingest_ridb", mode="record")


@shared_task
def places_monthly():
    raise NotImplementedError("apps.ingest.clients.places is still a stub (Phase 5).")
