"""Run the NPS connector only.

Refreshes fees for spots that already exist (created by seed_spots) — re-fetches each
one's /feespasses record and applies changes via promote_fields, which skips any spot
whose SpotCost has been hand-verified. Doesn't create new spots.
"""

from datetime import date
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand

from apps.catalog.models import Spot, SpotCost
from apps.core.revalidate import notify_revalidate
from apps.ingest.clients.nps import NPSClient
from apps.ingest.promote import promote_fields
from apps.ingest.staging import StagedRecord


class Command(BaseCommand):
    help = "Refresh NPS fee data for existing spots. Safe to re-run."

    def add_arguments(self, parser):
        parser.add_argument("--mode", choices=["record", "replay"], default="record")

    def handle(self, *args, **options):
        client = NPSClient(mode=options["mode"])
        changed = 0
        skipped = 0

        for spot in Spot.objects.filter(type=Spot.SpotType.NATIONAL_PARK):
            park_code = spot.slug.upper()
            payload = client.fees(park_code)
            StagedRecord.objects.create(
                source="nps_fees", external_id=park_code, raw_payload=payload
            )

            fee = self._extract_entrance_fee(payload)
            if fee is None:
                continue

            cost, _ = SpotCost.objects.get_or_create(spot=spot)
            result = promote_fields(
                cost,
                {
                    "entry_vehicle": fee,
                    "source_url": f"https://developer.nps.gov/api/v1/feespasses?parkCode={park_code}",
                    "verified_at": date.today(),
                },
            )
            if result.skipped_reason:
                skipped += 1
                continue
            if result.changed:
                cost.save()
                notify_revalidate("spot", spot.slug)
                changed += 1

        self.stdout.write(
            self.style.SUCCESS(f"Updated {changed} spots, skipped {skipped} (verified).")
        )

    @staticmethod
    def _extract_entrance_fee(fees_payload: dict) -> Decimal | None:
        results = fees_payload.get("data") or []
        if not results:
            return None
        fees = results[0].get("entranceFees") or []
        for fee in fees:
            if "vehicle" in (fee.get("title", "") + fee.get("description", "")).lower():
                cost = fee.get("cost")
                if cost:
                    try:
                        return Decimal(str(cost))
                    except InvalidOperation:
                        return None
        return None
