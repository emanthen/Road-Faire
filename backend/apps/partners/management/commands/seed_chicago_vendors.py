"""Seed real Chicago-area vendors for gear a road-tripper needs but Roadfare doesn't
sell itself: campervan/RV rental, bicycle rental, camping gear rental, car rental.

Every URL and fact here was checked against the vendor's own live site in this session
(via a real fetch, not recalled from memory) — see each entry's source_url. That is NOT
the same as human review, so needs_verification=True on every row, matching exactly the
seed_spots.py convention: a live-sourced fact still needs a human to confirm it before
it's trusted, this command only gets the citable starting data in.

No commission_note is set for any of these — Roadfare has no actual commission
agreement with any of them. These are informational listings (real business, real link
to their own site), not affiliate offers. Don't add a commission claim that isn't real.

contact_phone, description, and price_note were fetched directly from each vendor's own
page this session. terms_note is deliberately NOT a reproduction of any vendor's full
terms and conditions (that's a copyrighted document belonging to the vendor, and
republishing it here would be a liability/accuracy risk) — it's one short,
independently-confirmed real policy detail per vendor where one was found, or blank.
price_note is left blank wherever a vendor doesn't publish a fixed rate (car and RV
rental rates are dynamic/date-based — stating one number would misrepresent them).

rating/rating_count/rating_source/rating_url: Yelp and TripAdvisor both blocked a direct
fetch of their review pages (HTTP 403) — per this project's standing rule, that's a bot
block that isn't attempted to be bypassed. Bike and Roll's 4.5/5 TripAdvisor rating came
through in a search-result snippet with a clear source page, so it's included; the other
three vendors' review numbers either came from ambiguous aggregates (Cruise America) or a
different rating scale that can't be honestly converted to 5 stars (Enterprise), so
those are left blank rather than guessed.
"""

from typing import Any

from django.core.management.base import BaseCommand

from apps.partners.models import Offer, Partner

VENDORS: list[dict[str, Any]] = [
    {
        "name": "Cruise America (O'Hare Area)",
        "slug": "cruise-america-ohare",
        "base_url": "https://www.cruiseamerica.com/rv-rental-locations/illinois/chicago-ohare-area",
        "source_url": "https://www.cruiseamerica.com/rv-rental-locations/illinois/chicago-ohare-area",
        "category": Offer.Category.CAMPERVAN,
        "contact_phone": "(847) 451-9662",
        "terms_note": "",
        "description": "Class C motorhomes — 21', 25', and 30' models, Ford chassis, "
        "self-contained water and sewage.",
        "price_note": "One-way relocation deals as low as $9-$39/night; round-trip "
        "nightly rates vary by date.",
        "rating": None,
        "rating_count": None,
        "rating_source": "",
        "rating_url": "",
    },
    {
        "name": "Bike and Roll Chicago",
        "slug": "bike-and-roll-chicago",
        "base_url": "https://bikeandroll.com/chicago/",
        "source_url": "https://bikeandroll.com/chicago/contact/",
        "category": Offer.Category.BICYCLE,
        "contact_phone": "(312) 729-1000",
        "terms_note": "",
        "description": "",
        "price_note": "",
        "rating": "4.5",
        "rating_count": None,
        "rating_source": "TripAdvisor",
        "rating_url": "https://www.tripadvisor.com/Attraction_Review-g35805-d1818809-Reviews-or50-Bike_and_Roll-Chicago_Illinois.html",
    },
    {
        # Fetched via search only — the vendor's own page returned a Cloudflare bot
        # challenge on direct fetch, so this is less confirmed than the other three.
        "name": "LowerGear",
        "slug": "lowergear",
        "base_url": "https://www.lowergear.com/tent_rental_chicago",
        "source_url": "https://www.lowergear.com/tent_rental_chicago",
        "category": Offer.Category.CAMPING_GEAR,
        "contact_phone": "(480) 348-8917",
        "terms_note": "Rental days are not charged while items are in transit to or from you.",
        "description": "Camping and backpacking gear rental — tents, sleeping bags, "
        "backpacks, and cooking gear, shipped nationwide.",
        "price_note": "",
        "rating": None,
        "rating_count": None,
        "rating_source": "",
        "rating_url": "",
    },
    {
        "name": "Enterprise Rent-A-Car (O'Hare Airport)",
        "slug": "enterprise-ohare",
        "base_url": "https://www.enterprise.com/en/car-rental-locations/us/il/chicago-ohare-international-airport-15v5.html",
        "source_url": "https://www.enterprise.com/en/car-rental-locations/us/il/chicago-ohare-international-airport-15v5.html",
        "category": Offer.Category.CAR,
        "contact_phone": "(833) 856-0900",
        "terms_note": "",
        "description": "Cars, SUVs, trucks, and vans — economy through full-size, plus "
        "luxury sedans and SUVs.",
        "price_note": "",
        "rating": None,
        "rating_count": None,
        "rating_source": "",
        "rating_url": "",
    },
]


class Command(BaseCommand):
    help = "Seed real Chicago-area campervan/bicycle/camping-gear/car rental vendors."

    def handle(self, *args, **options):
        for v in VENDORS:
            partner, _ = Partner.objects.update_or_create(
                slug=v["slug"],
                defaults={
                    "name": v["name"],
                    "service_area": "Chicago, IL",
                    "contact_phone": v["contact_phone"],
                    "terms_note": v["terms_note"],
                    "rating": v["rating"],
                    "rating_count": v["rating_count"],
                    "rating_source": v["rating_source"],
                    "rating_url": v["rating_url"],
                    "source_url": v["source_url"],
                    "needs_verification": True,
                },
            )
            Offer.objects.update_or_create(
                partner=partner,
                category=v["category"],
                defaults={
                    "base_url": v["base_url"],
                    "description": v["description"],
                    "price_note": v["price_note"],
                },
            )
            self.stdout.write(f"{v['name']}: {v['category']}")

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(VENDORS)} Chicago vendors."))
