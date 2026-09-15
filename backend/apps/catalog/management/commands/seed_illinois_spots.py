"""Seed two real Illinois NPS units, fetched directly from their own nps.gov pages
this session: Pullman National Historical Park and Lincoln Home National Historic
Site. Same discipline as seed_spot_details — an AI fetch is not human review, so
every row lands with needs_verification=True.

Both units are free to enter (confirmed on their fee pages) and sit on flat Chicago-
area/Springfield terrain, so elevation_ft and a citable best-time-to-visit window are
left blank rather than guessed — no such fact was found stated on nps.gov for either.
"""

from decimal import Decimal
from typing import Any

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import Photo, Region, Spot, SpotCost, State

PHOTO_CREDIT = "National Park Service"
PHOTO_LICENSE = "Public domain (17 U.S.C. § 105)"

# slug -> full seed data, every fact sourced from the listed source_url this session.
SPOTS: dict[str, dict[str, Any]] = {
    "pull": {
        "name": "Pullman National Historical Park",
        "lat": 41.6906,
        "lon": -87.6067,
        "type": Spot.SpotType.MONUMENT,
        "blurb": "A planned 1880s company town on Chicago's Far South Side, built by "
        "George Pullman for workers making his railroad sleeping cars — now a National "
        "Historical Park telling that history and the 1894 Pullman Strike.",
        "highlights": "The restored Clock Tower and Administration Building, rowhouses "
        "and public buildings from the original company town, and exhibits on the 1894 "
        "Pullman Strike and the Pullman porters' role in the labor movement.",
        "best_time_to_visit": "",
        "contact_phone": "(773) 928-7257",
        "source_url": "https://www.nps.gov/pull/planyourvisit/fees.htm",
        "photo_alt": "Pullman National Historical Park",
    },
    "liho": {
        "name": "Lincoln Home National Historic Site",
        "lat": 39.7999,
        "lon": -89.6438,
        "type": Spot.SpotType.MONUMENT,
        "blurb": "The only home Abraham Lincoln ever owned, in Springfield, Illinois, "
        "preserved with the surrounding historic neighborhood as it looked when the "
        "Lincoln family lived there before he became president.",
        "highlights": "Ranger-guided tours of the Lincoln family's furnished home, plus "
        "the surrounding four-block historic neighborhood of preserved period houses.",
        "best_time_to_visit": "",
        "contact_phone": "(217) 492-4241",
        "source_url": "https://www.nps.gov/liho/planyourvisit/fees.htm",
        "photo_alt": "Lincoln Home National Historic Site",
    },
}


class Command(BaseCommand):
    help = "Seed two real, free-admission Illinois NPS units (Pullman, Lincoln Home)."

    @transaction.atomic
    def handle(self, *args, **options):
        region, _ = Region.objects.get_or_create(name="Demo", defaults={"slug": "demo"})
        state, _ = State.objects.get_or_create(
            abbreviation="IL", defaults={"name": "Illinois", "region": region}
        )

        seeded = []
        for slug, data in SPOTS.items():
            spot, _ = Spot.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": data["name"],
                    "state": state,
                    "type": data["type"],
                    "geom": Point(data["lon"], data["lat"]),
                    "min_days": 1,
                    "blurb": data["blurb"],
                    "highlights": data["highlights"],
                    "elevation_ft": None,
                    "best_time_to_visit": data["best_time_to_visit"],
                    "contact_phone": data["contact_phone"],
                    "vibe_tags": ["history", "free-admission"],
                    "meta_title": f"{data['name']} — cost, fees, and best time to visit"[:70],
                    "meta_description": data["highlights"][:157] + "..."
                    if len(data["highlights"]) > 160
                    else data["highlights"],
                    "source_url": data["source_url"],
                    "needs_verification": True,
                },
            )
            SpotCost.objects.update_or_create(
                spot=spot,
                defaults={
                    "entry_vehicle": Decimal("0.00"),
                    "source_url": data["source_url"],
                    "needs_verification": True,
                },
            )
            Photo.objects.update_or_create(
                spot=spot,
                source="nps.gov",
                s3_key=f"/images/parks/{slug}.jpg",
                defaults={
                    "credit": PHOTO_CREDIT,
                    "license": PHOTO_LICENSE,
                    "alt_text": data["photo_alt"],
                    "is_primary": True,
                    "sort_order": 0,
                },
            )
            Photo.objects.update_or_create(
                spot=spot,
                source="nps.gov",
                s3_key=f"/images/parks-2/{slug}.jpg",
                defaults={
                    "credit": PHOTO_CREDIT,
                    "license": PHOTO_LICENSE,
                    "alt_text": data["photo_alt"],
                    "is_primary": False,
                    "sort_order": 1,
                },
            )
            seeded.append(data["name"])

        self.stdout.write(
            self.style.SUCCESS(f"Seeded {len(seeded)} Illinois spots: " + ", ".join(seeded))
        )
