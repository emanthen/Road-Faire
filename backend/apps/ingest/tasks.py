"""Celery beat: nps_daily, ridb_daily, places_monthly, eia_fuel_weekly.

Task bodies just call the management commands (or, for eia_fuel_weekly, the same
function the request path calls) so the logic has one home.
"""

from celery import shared_task
from django.conf import settings
from django.core.management import call_command


@shared_task
def nps_daily():
    call_command("ingest_nps", mode="record")


@shared_task
def ridb_daily():
    call_command("ingest_ridb", mode="record")


def _refresh_spot_phone(client, spot) -> bool:
    """One spot's worth of places_monthly, factored out so tests can drive it with a
    replay-mode client the way apps.ingest.tests.test_idempotent drives seed_spots'
    _seed_one() — without the task's hardcoded record-mode client and DB-wide loop.
    Returns whether spot.contact_phone changed (and was saved)."""
    from apps.ingest.promote import promote_fields
    from apps.ingest.staging import StagedRecord

    candidates = client.find_place(f"{spot.name} visitor center").get("candidates") or []
    if not candidates:
        return False
    place_id = candidates[0]["place_id"]

    payload = client.details(place_id)
    StagedRecord.objects.create(source="places", external_id=place_id, raw_payload=payload)

    phone = payload.get("result", {}).get("formatted_phone_number")
    if not phone:
        return False
    result = promote_fields(spot, {"contact_phone": phone})
    if result.changed:
        spot.save()
    return result.changed


@shared_task
def places_monthly():
    """Refreshes Spot.contact_phone from Google Places' formatted_phone_number,
    respecting is_manually_verified — same promote_fields()-guarded pattern as
    ingest_nps's fee refresh. No-ops when GOOGLE_PLACES_API_KEY isn't configured,
    same as every other optional external source in this app."""
    if not settings.GOOGLE_PLACES_API_KEY:
        return

    from apps.catalog.models import Spot
    from apps.ingest.clients.places import PlacesClient

    client = PlacesClient(mode="record")
    for spot in Spot.objects.all():
        _refresh_spot_phone(client, spot)


@shared_task
def eia_fuel_weekly():
    """Pre-warms apps.planner.fuel's weekly cache so the first /api/plan request of
    the week doesn't pay EIA's fetch latency. Not the only place the cache gets
    populated — current_fuel_price_per_gallon() also fetches lazily on a cache miss —
    this just keeps it warm proactively."""
    from apps.planner.fuel import current_fuel_price_per_gallon

    current_fuel_price_per_gallon()
