"""Ingest campervan-relevant amenities (dump stations, potable water) near every seeded
Spot from OpenStreetMap/Overpass — no API key needed, ODbL-licensed and citable. Every
row lands with needs_verification=True: this is raw OSM data, not hand-checked.

Re-running replaces a spot's rows for a given kind rather than accumulating duplicates —
OSM node positions can shift or disappear, so "refresh from source" is the right
semantics here, unlike Spot itself where a re-run must not clobber hand-verified fields.
"""

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import Spot, SpotAmenity
from apps.ingest.clients.overpass import OverpassClient

OSM_ATTRIBUTION_URL = "https://www.openstreetmap.org/copyright"
DUMP_STATION_RADIUS_M = 20000
WATER_RADIUS_M = 5000


class Command(BaseCommand):
    help = "Ingest dump stations and potable water points near every Spot from Overpass."

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode",
            choices=["record", "replay"],
            default="record",
            help="record = hit the live Overpass API and save fixtures; "
            "replay = use saved fixtures.",
        )

    def handle(self, *args, **options):
        client = OverpassClient(mode=options["mode"])
        spots = list(Spot.objects.all())
        if not spots:
            self.stdout.write(self.style.WARNING("No spots in the database — nothing to do."))
            return

        total = 0
        for spot in spots:
            try:
                total += self._ingest_kind(
                    client, spot, SpotAmenity.Kind.DUMP_STATION,
                    client.dump_stations_near(spot.geom.y, spot.geom.x, DUMP_STATION_RADIUS_M),
                )
                total += self._ingest_kind(
                    client, spot, SpotAmenity.Kind.WATER,
                    client.water_near(spot.geom.y, spot.geom.x, WATER_RADIUS_M),
                )
            except Exception as exc:  # noqa: BLE001 — one bad spot shouldn't kill the run
                self.stderr.write(self.style.ERROR(f"{spot.slug}: {exc}"))

        self.stdout.write(self.style.SUCCESS(f"Ingested {total} amenities."))

    @transaction.atomic
    def _ingest_kind(
        self, client: OverpassClient, spot: Spot, kind: str, payload: dict
    ) -> int:
        elements = payload.get("elements") or []
        SpotAmenity.objects.filter(spot=spot, kind=kind).delete()
        rows = [
            SpotAmenity(
                spot=spot,
                kind=kind,
                geom=Point(element["lon"], element["lat"]),
                source_url=OSM_ATTRIBUTION_URL,
                needs_verification=True,
            )
            for element in elements
            if element.get("type") == "node"
        ]
        SpotAmenity.objects.bulk_create(rows)
        return len(rows)
