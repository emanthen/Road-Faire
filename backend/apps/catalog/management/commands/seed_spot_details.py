"""Enrich the 11 demo spots (seeded by seed_demo_data) with real content fetched
directly from each park's own nps.gov pages this session: elevation of the highest
point, a best-time-to-visit note, a highlights paragraph, and category tags derived
from that same real content.

This is an AI fetch, not human review, so every row still lands with
needs_verification=True — same discipline as seed_spots and seed_chicago_vendors: a
live-sourced fact needs a human to confirm it before it's trusted. Where NPS's own
pages didn't state a fact plainly (e.g. Acadia's exact best-time window), only what was
actually confirmed is included — nothing here is estimated or invented to fill a gap.

source_url points at the specific nps.gov page the facts were fetched from, not just
the park's homepage, so a reviewer can check the same page.
"""

from django.core.management.base import BaseCommand

from apps.catalog.models import Photo, Spot

# slug -> (elevation_ft, elevation source url, best_time_to_visit, highlights, vibe_tags)
DETAILS = {
    "acad": (
        1530,
        "https://www.nps.gov/places/cadillac-mountain.htm",
        "Fall, for foliage — peak color generally comes in mid-October.",
        "The highest rocky headlands on the US Atlantic coast, with over 158 miles of "
        "hiking trails, 45 miles of historic carriage roads, Sand Beach, and Thunder "
        "Hole's crashing waves at high tide.",
        ["coastal", "hiking", "carriage-roads"],
    ),
    "brca": (
        9115,
        "https://www.nps.gov/places/000/rainbow-point.htm",
        "Fall and spring, for fewer crowds and cooler temperatures.",
        "The largest concentration of hoodoos in the world, densely packed within the "
        "Bryce Amphitheater — pinnacles and spires left standing by erosion.",
        ["hoodoos", "hiking", "high-elevation"],
    ),
    "ever": (
        # No natural high point in feet was found stated plainly on nps.gov (Everglades
        # is famously near-flat) — left null rather than guessed, per the "never guess
        # a real-world fact" rule. The 70ft Shark Valley Observation Tower figure found
        # during research is a built structure's height, not the park's elevation, so
        # it isn't a substitute.
        None,
        "https://www.nps.gov/ever/planyourvisit/weather.htm",
        "December through April, the dry season — cooler, less humid, and easier "
        "wildlife viewing than the hot, mosquito-heavy wet season.",
        "Navigable waters cover a third of the park: boating, paddling trails, bird "
        "watching, and alligators visible in their natural habitat.",
        ["wetlands", "wildlife", "boating"],
    ),
    "glac": (
        10448,
        "https://www.nps.gov/glac/learn/news/fact-sheet.htm",
        "Once Going-to-the-Sun Road fully opens, typically mid-to-late June "
        "(the exact date varies year to year with snowpack).",
        "734 miles of alpine hiking trails, ranger-led boat tours and talks, and the "
        "Going-to-the-Sun Road scenic drive.",
        ["mountains", "hiking", "glaciers"],
    ),
    "grca": (
        7000,
        "https://www.nps.gov/grca/planyourvisit/basicinfo.htm",
        "November through February is the least crowded; spring break and summer are "
        "the busiest.",
        "Rim trails and scenic overlooks along Desert View Drive, mule trips, Colorado "
        "River rafting, and the historic Grand Canyon Railway.",
        ["canyon", "hiking", "rafting"],
    ),
    "grte": (
        13770,
        "https://www.nps.gov/places/000/grand-teton.htm",
        "May through September, when most park roads and facilities are open.",
        "The Teton Range towering over Jackson Hole, with hiking, climbing, boating, "
        "and moose and grizzly bear viewing.",
        ["mountains", "wildlife", "climbing"],
    ),
    "romo": (
        12183,
        "https://www.nps.gov/romo/planyourvisit/trail_ridge_road.htm",
        "Late May through September, once Trail Ridge Road — the highest continuous "
        "paved road in the US — opens for the season (exact dates vary with snowpack).",
        "Over 350 miles of trails, alpine tundra crossed by Trail Ridge Road, and "
        "wildlife viewing throughout the park.",
        ["mountains", "hiking", "alpine-tundra"],
    ),
    "seki": (
        14505,
        "https://www.nps.gov/seki/planyourvisit/whitney.htm",
        "Varies by elevation — the giant sequoia groves are accessible most of the "
        "year, but snow can close the Generals Highway between the parks in winter.",
        "Towering giant sequoias, Sierra Nevada wilderness, and Mount Whitney — the "
        "highest peak in the contiguous US — on the parks' eastern boundary.",
        ["giant-sequoias", "mountains", "hiking"],
    ),
    "yell": (
        11358,
        "https://www.nps.gov/yell/planyourvisit/parkfacts.htm",
        "Late April through October, when most park facilities are open (services are "
        "limited from early November through late April).",
        "Boardwalks past hot springs, mudpots, and geysers, over 1,100 miles of trails, "
        "and bison and bears visible throughout the park.",
        ["geysers", "wildlife", "hiking"],
    ),
    "yose": (
        8800,
        "https://www.nps.gov/yose/planyourvisit/halfdome.htm",
        "Late May through mid-October, when the Half Dome cables are up and most "
        "high-country roads are open.",
        "Over 750 miles of trails, El Capitan and Half Dome, waterfalls along the "
        "Merced River, and Yosemite Valley.",
        ["waterfalls", "climbing", "hiking"],
    ),
    "zion": (
        8726,
        "https://www.nps.gov/im/ncpn/bpd-zion.htm",
        None,
        "Towering red cliffs and canyon trails, including the Virgin River Narrows "
        "hike between steep canyon walls.",
        ["canyon", "narrows-hiking", "red-rock"],
    ),
}

PHOTO_CREDIT = "National Park Service"
PHOTO_LICENSE = "Public domain (17 U.S.C. § 105)"


class Command(BaseCommand):
    help = "Enrich the 11 demo spots with real nps.gov content: elevation, best time, tags, photos."

    def handle(self, *args, **options):
        updated = 0
        for slug, (elevation_ft, source_url, best_time, highlights, tags) in DETAILS.items():
            try:
                spot = Spot.objects.get(slug=slug)
            except Spot.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Skipping {slug}: no such spot (run seed_demo_data first).")
                )
                continue

            spot.elevation_ft = elevation_ft
            spot.best_time_to_visit = best_time or ""
            spot.highlights = highlights
            spot.vibe_tags = tags
            spot.source_url = source_url
            spot.needs_verification = True
            spot.meta_title = f"{spot.name} — cost, fees, and best time to visit"[:70]
            spot.meta_description = (
                highlights[:157] + "..." if len(highlights) > 160 else highlights
            )
            spot.save()

            Photo.objects.update_or_create(
                spot=spot,
                source="nps.gov",
                s3_key=f"/images/parks/{slug}.jpg",
                defaults={
                    "credit": PHOTO_CREDIT,
                    "license": PHOTO_LICENSE,
                    "alt_text": f"{spot.name} National Park",
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
                    "alt_text": f"{spot.name} National Park",
                    "is_primary": False,
                    "sort_order": 1,
                },
            )
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Enriched {updated} spots with real content."))
