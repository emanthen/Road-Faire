"""Run the RIDB connector only.

For each seeded national park spot, searches RIDB for a matching facility and records
its permit-entrance (timed-entry) data as a ReservationRule, respecting is_manually_verified.
RIDB's facility search is name-based (there's no NPS<->RIDB code crosswalk in the free
API), so this takes the first match — good enough to seed timed-entry rules for a hand-
curated 25-spot catalog, not a robust matching strategy at scale.
"""

from datetime import date

from django.core.management.base import BaseCommand

from apps.catalog.models import ReservationRule, Spot
from apps.ingest.clients.ridb import RIDBClient
from apps.ingest.promote import promote_fields
from apps.ingest.staging import StagedRecord


class Command(BaseCommand):
    help = "Refresh RIDB timed-entry/permit data for existing spots. Safe to re-run."

    def add_arguments(self, parser):
        parser.add_argument("--mode", choices=["record", "replay"], default="record")

    def handle(self, *args, **options):
        client = RIDBClient(mode=options["mode"])
        changed = 0

        for spot in Spot.objects.filter(type=Spot.SpotType.NATIONAL_PARK):
            search = client.facilities(spot.name)
            StagedRecord.objects.create(
                source="ridb_facilities", external_id=spot.slug, raw_payload=search
            )
            facility = self._first_facility(search)
            if facility is None:
                continue

            entrances = client.permit_entrances(facility["FacilityID"])
            StagedRecord.objects.create(
                source="ridb_permitentrances",
                external_id=facility["FacilityID"],
                raw_payload=entrances,
            )
            if not entrances.get("RECDATA"):
                continue

            rule, _ = ReservationRule.objects.get_or_create(
                spot=spot,
                kind=ReservationRule.Kind.TIMED_ENTRY,
                defaults={"source_url": f"https://ridb.recreation.gov/api/v1/facilities/{facility['FacilityID']}"},
            )
            result = promote_fields(
                rule,
                {
                    "booking_url": facility.get("FacilityReservationURL", ""),
                    "verified_at": date.today(),
                },
            )
            if result.changed:
                rule.save()
                changed += 1

        self.stdout.write(self.style.SUCCESS(f"Updated {changed} reservation rules."))

    @staticmethod
    def _first_facility(search_payload: dict) -> dict | None:
        results = search_payload.get("RECDATA") or []
        return results[0] if results else None
