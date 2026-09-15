"""Load the hand-verified starter 25 spots.

Pulls each spot's data live from the NPS API (park record + fees) rather than typing
remembered figures into the DB, per BUILD_PROMPT §0 rule 3 ("if you cannot cite it, do
not store it"). Every row lands with is_manually_verified=False, needs_verification=True
— a human still has to check each one before it's trusted; this command only gets the
citable starting data in, it doesn't mark anything verified.

The list below is a curation choice (which park codes to seed), not a factual claim
about any park's fees or rules.
"""

from datetime import date
from decimal import Decimal, InvalidOperation

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import Region, Spot, SpotCost, State
from apps.ingest.clients.nps import NPSClient
from apps.ingest.promote import promote_fields
from apps.ingest.staging import StagedRecord

# The 11 non-resident-surcharge parks (BUILD_PROMPT §1) plus 14 more well-known NPS units
# chosen for driving-loop variety around major airports. Codes only — every fact about
# each park comes from the live NPS response, not from this list.
SEED_PARK_CODES = [
    # -- surcharge parks --
    "ACAD", "BRCA", "EVER", "GLAC", "GRCA", "GRTE", "ROMO", "SEKI", "YELL", "YOSE", "ZION",
    # -- additional seed spots --
    "JOTR", "ARCH", "CANY", "CARE", "DEVA", "OLYM", "MORA", "NOCA", "GRSM", "SHEN",
    "REDW", "BIBE", "BADL", "CRLA",
]

DEFAULT_REGION_NAME = "Unsorted"


class Command(BaseCommand):
    help = "Seed the starter 25 spots from the live NPS API. Flags every row for manual review."

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode",
            choices=["record", "replay"],
            default="record",
            help="record = hit the live NPS API and save fixtures; replay = use saved fixtures.",
        )

    def handle(self, *args, **options):
        client = NPSClient(mode=options["mode"])
        needs_review = []

        for park_code in SEED_PARK_CODES:
            try:
                spot = self._seed_one(client, park_code)
                if spot:
                    needs_review.append(spot.name)
            except Exception as exc:  # noqa: BLE001 — one bad park shouldn't kill the run
                self.stderr.write(self.style.ERROR(f"{park_code}: {exc}"))

        self.stdout.write(self.style.SUCCESS(f"Seeded/updated {len(needs_review)} spots."))
        self.stdout.write("Needs manual review (needs_verification=True):")
        for name in needs_review:
            self.stdout.write(f"  - {name}")

    @transaction.atomic
    def _seed_one(self, client: NPSClient, park_code: str) -> Spot | None:
        park_payload = client.park(park_code)
        StagedRecord.objects.create(
            source="nps_park", external_id=park_code, raw_payload=park_payload
        )
        results = park_payload.get("data") or []
        if not results:
            self.stderr.write(self.style.WARNING(f"{park_code}: no park data returned"))
            return None
        park = results[0]

        fees_payload = client.fees(park_code)
        StagedRecord.objects.create(
            source="nps_fees", external_id=park_code, raw_payload=fees_payload
        )

        region, _ = Region.objects.get_or_create(
            name=DEFAULT_REGION_NAME, defaults={"slug": "unsorted"}
        )
        state_abbr = (park.get("states") or "").split(",")[0].strip() or "XX"
        state, _ = State.objects.get_or_create(
            abbreviation=state_abbr, defaults={"name": state_abbr, "region": region}
        )

        lat = self._to_decimal(park.get("latitude"))
        lon = self._to_decimal(park.get("longitude"))
        if lat is None or lon is None:
            self.stderr.write(self.style.WARNING(f"{park_code}: missing coordinates"))
            return None

        # get_or_create (not update_or_create) + promote_fields: a re-run must not
        # blind-overwrite a spot the user has since hand-verified (BUILD_PROMPT §3).
        spot, created = Spot.objects.get_or_create(
            slug=park_code.lower(),
            defaults={
                "name": park.get("fullName", park_code),
                "state": state,
                "type": Spot.SpotType.NATIONAL_PARK,
                "geom": Point(float(lon), float(lat)),
                "needs_verification": True,
            },
        )
        promote_fields(
            spot,
            {
                "name": park.get("fullName", park_code),
                "state": state,
                "geom": Point(float(lon), float(lat)),
                "blurb": (park.get("description") or "")[:2000],
                "source_url": f"https://developer.nps.gov/api/v1/parks?parkCode={park_code}",
                "verified_at": date.today(),
            },
        )
        spot.save()

        entrance_fees = self._extract_entrance_fee(fees_payload)
        if entrance_fees is not None:
            cost, _ = SpotCost.objects.get_or_create(
                spot=spot, defaults={"needs_verification": True}
            )
            promote_fields(
                cost,
                {
                    "entry_vehicle": entrance_fees,
                    "source_url": f"https://developer.nps.gov/api/v1/feespasses?parkCode={park_code}",
                    "verified_at": date.today(),
                },
            )
            cost.save()

        return spot

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        if not value:
            return None
        try:
            return Decimal(str(value))
        except InvalidOperation:
            return None

    @staticmethod
    def _extract_entrance_fee(fees_payload: dict) -> Decimal | None:
        results = fees_payload.get("data") or []
        if not results:
            return None
        fees = results[0].get("entranceFees") or []
        for fee in fees:
            if fee.get("title", "").lower().startswith("vehicle") or "vehicle" in fee.get(
                "description", ""
            ).lower():
                cost = fee.get("cost")
                if cost:
                    try:
                        return Decimal(str(cost))
                    except InvalidOperation:
                        return None
        return None
