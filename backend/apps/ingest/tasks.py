"""Celery beat: nps_daily, ridb_daily, places_monthly, eia_fuel_weekly.

Task bodies just call the management commands (or, for eia_fuel_weekly, the same
function the request path calls) so the logic has one home.
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


@shared_task
def eia_fuel_weekly():
    """Pre-warms apps.planner.fuel's weekly cache so the first /api/plan request of
    the week doesn't pay EIA's fetch latency. Not the only place the cache gets
    populated — current_fuel_price_per_gallon() also fetches lazily on a cache miss —
    this just keeps it warm proactively."""
    from apps.planner.fuel import current_fuel_price_per_gallon

    current_fuel_price_per_gallon()
