"""Bulk-load NOAA 1991-2020 climate normals.

Needs a spot-slug -> NOAA station ID mapping to know which station is "nearest" each
spot. I'm not confident enough in specific NOAA station IDs recalled from memory to
hardcode them here (a wrong ID either 404s, caught below, or worse — silently loads the
wrong station's climate for a spot; BUILD_PROMPT §9: "do not guess"). This command takes
that mapping as an explicit --station-map JSON file (`{"yell": "USW00024011", ...}`)
instead: sourcing accurate stations (e.g. via NOAA's station-search API, nearest to each
Spot.geom) is real work still to do, not something to fake here.
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.catalog.models import ClimateNormal, Spot
from apps.ingest.clients.noaa import NOAAClient


class Command(BaseCommand):
    help = "Load NOAA 1991-2020 monthly climate normals for spots given a station-map file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--station-map", required=True, help="Path to a JSON {slug: station_id} file."
        )
        parser.add_argument("--mode", choices=["record", "replay"], default="record")

    def handle(self, *args, **options):
        station_map_path = Path(options["station_map"])
        if not station_map_path.exists():
            raise CommandError(f"No such file: {station_map_path}")
        station_map: dict[str, str] = json.loads(station_map_path.read_text(encoding="utf-8"))

        client = NOAAClient(mode=options["mode"])
        loaded = 0

        for slug, station_id in station_map.items():
            try:
                spot = Spot.objects.get(slug=slug)
            except Spot.DoesNotExist:
                self.stderr.write(self.style.WARNING(f"No spot with slug '{slug}', skipping"))
                continue

            try:
                months = client.monthly_normals(station_id)
            except Exception as exc:  # noqa: BLE001 — one bad station shouldn't kill the run
                self.stderr.write(self.style.ERROR(f"{slug} ({station_id}): {exc}"))
                continue

            for month_data in months:
                if not month_data.get("high_f") or not month_data.get("low_f"):
                    continue
                ClimateNormal.objects.update_or_create(
                    spot=spot,
                    month=month_data["month"],
                    defaults={
                        "high_f": month_data["high_f"],
                        "low_f": month_data["low_f"],
                        "precip_in": month_data.get("precip_in") or 0,
                        "snow_in": month_data.get("snow_in") or 0,
                    },
                )
            loaded += 1

        self.stdout.write(self.style.SUCCESS(f"Loaded climate normals for {loaded} spots."))
