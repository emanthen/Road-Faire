"""Precompute the airport -> spot drive-time matrix."""

from django.core.management.base import BaseCommand

from apps.catalog.models import DriveTime, Spot
from apps.ingest.clients.osrm import DriveTimeClient, DriveTimeUnavailable
from apps.planner.engine.candidates import AIRPORTS


class Command(BaseCommand):
    help = "Populate DriveTime for every airport x spot pair. Safe to re-run."

    def add_arguments(self, parser):
        parser.add_argument("--mode", choices=["record", "replay"], default="record")

    def handle(self, *args, **options):
        client = DriveTimeClient(mode=options["mode"])
        spots = list(Spot.objects.all())
        written = 0
        skipped = 0

        for code, (lat, lon) in AIRPORTS.items():
            for spot in spots:
                try:
                    minutes, miles = client.drive_time((lat, lon), (spot.geom.y, spot.geom.x))
                except DriveTimeUnavailable:
                    skipped += 1
                    continue
                DriveTime.objects.update_or_create(
                    origin_code=code,
                    spot=spot,
                    defaults={"minutes": minutes, "miles": miles},
                )
                written += 1

        self.stdout.write(self.style.SUCCESS(f"Wrote {written} drive times, skipped {skipped}."))
