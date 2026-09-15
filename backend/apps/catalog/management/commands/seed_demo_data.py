"""Seed the 11 non-resident-surcharge parks with real names and approximate coordinates
so /spots, /guides-adjacent pages, and the planner have something to show locally without
a live NPS_API_KEY.

This is NOT the citable, per-park-verified pipeline `seed_spots` is (that one pulls fees
live from NPS and is the one that matters for production data quality). Every fee value
here is the SAME placeholder assumption already used elsewhere in this codebase
(apps.fees.constants / the frontend's ASSUMED_VEHICLE_FEE), not a claim about any
specific park's real entrance fee. Every row lands with needs_verification=True and a
[DEMO] marker in its blurb so it can never be mistaken for verified data, and is easy to
find and delete once real ingestion (seed_spots) is possible.

Coordinates are approximate (best general knowledge, same epistemic status as the
AIRPORTS reference dict in apps.planner.engine.candidates), not survey-precise.
"""

from decimal import Decimal

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import Activity, ClimateNormal, CrowdIndex, Region, Spot, SpotCost, State

DEMO_MARKER = "[DEMO DATA — not independently verified]"
ASSUMED_VEHICLE_FEE = Decimal("35.00")
FEE_SOURCE_URL = "https://www.nps.gov/aboutus/entrance-fee-prices.htm"

# One flat placeholder climate/crowd profile reused for every month at every demo spot —
# NOT a claim about any park's real seasonal weather (that's NOAA 1991-2020 normals,
# apps.ingest.clients.noaa, a real per-station pipeline). This exists only so
# apps.catalog.scoring.month_score() has something to score instead of correctly
# returning 0 for "no data", which otherwise filters every demo spot out of the planner.
PLACEHOLDER_HIGH_F = Decimal("70.0")
PLACEHOLDER_LOW_F = Decimal("50.0")
PLACEHOLDER_PRECIP_IN = Decimal("2.0")
PLACEHOLDER_CROWD_SCORE = 50

# name, slug, state abbreviation, state name, lat, lon
PARKS = [
    ("Acadia", "acad", "ME", "Maine", 44.35, -68.21),
    ("Bryce Canyon", "brca", "UT", "Utah", 37.59, -112.19),
    ("Everglades", "ever", "FL", "Florida", 25.29, -80.90),
    ("Glacier", "glac", "MT", "Montana", 48.70, -113.72),
    ("Grand Canyon", "grca", "AZ", "Arizona", 36.11, -112.11),
    ("Grand Teton", "grte", "WY", "Wyoming", 43.79, -110.68),
    ("Rocky Mountain", "romo", "CO", "Colorado", 40.34, -105.68),
    ("Sequoia & Kings Canyon", "seki", "CA", "California", 36.49, -118.57),
    ("Yellowstone", "yell", "WY", "Wyoming", 44.43, -110.59),
    ("Yosemite", "yose", "CA", "California", 37.87, -119.54),
    ("Zion", "zion", "UT", "Utah", 37.30, -113.03),
]


class Command(BaseCommand):
    help = (
        "Seed the 11 surcharge parks with placeholder demo data for local development. "
        "Not a substitute for seed_spots (the real, NPS-sourced pipeline)."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        region, _ = Region.objects.get_or_create(
            name="Demo", defaults={"slug": "demo"}
        )

        seeded = []
        for name, slug, state_abbr, state_name, lat, lon in PARKS:
            state, _ = State.objects.get_or_create(
                abbreviation=state_abbr, defaults={"name": state_name, "region": region}
            )
            spot, created = Spot.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "state": state,
                    "type": Spot.SpotType.NATIONAL_PARK,
                    "geom": Point(lon, lat),
                    "min_days": 2,
                    "blurb": f"{DEMO_MARKER} A US national park that charges the "
                    "non-resident surcharge.",
                    "needs_verification": True,
                },
            )
            SpotCost.objects.update_or_create(
                spot=spot,
                defaults={
                    "entry_vehicle": ASSUMED_VEHICLE_FEE,
                    "source_url": FEE_SOURCE_URL,
                    "needs_verification": True,
                },
            )
            Activity.objects.get_or_create(
                spot=spot,
                name="Visitor center loop trail",
                defaults={"kind": Activity.Kind.TRAIL},
            )
            for month in range(1, 13):
                ClimateNormal.objects.update_or_create(
                    spot=spot,
                    month=month,
                    defaults={
                        "high_f": PLACEHOLDER_HIGH_F,
                        "low_f": PLACEHOLDER_LOW_F,
                        "precip_in": PLACEHOLDER_PRECIP_IN,
                    },
                )
                CrowdIndex.objects.update_or_create(
                    spot=spot, month=month, defaults={"score": PLACEHOLDER_CROWD_SCORE}
                )
            seeded.append(name)

        self.stdout.write(
            self.style.WARNING(
                f"Seeded {len(seeded)} DEMO spots (placeholder fees, needs_verification=True): "
                + ", ".join(seeded)
            )
        )
