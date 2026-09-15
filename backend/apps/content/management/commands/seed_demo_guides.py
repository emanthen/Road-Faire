"""Seed a few real editorial pages for /guides.

Unlike apps.catalog's demo seed, this isn't a placeholder for missing third-party data —
these are first-party explainers about how Roadfare itself works (the surcharge math,
the pass-vs-pay-as-you-go tradeoff, the itemised cost model), so every claim in them is
something this codebase actually does, not a fact about a park that needs a citation.
"""

from django.core.management.base import BaseCommand

from apps.content.models import Page

PAGES = [
    {
        "slug": "non-resident-surcharge-explained",
        "title": "How the non-resident surcharge actually works",
        "body": (
            "Eleven US national parks charge non-US residents an extra $100 per adult "
            "on top of the standard entrance fee. It applies per person, not per "
            "vehicle, and it stacks: two non-resident adults visiting three surcharge "
            "parks owe $600 in surcharges alone, on top of whatever the parks "
            "themselves charge to get in.\n\n"
            "An America the Beautiful annual pass sidesteps it differently depending "
            "on residency. A US resident's pass covers the whole vehicle at $80, so it "
            "wipes out the surcharge question entirely. A non-resident's pass costs "
            "$250, but it only exempts the person it's issued to, so a family still "
            "needs one pass per adult to fully avoid the surcharge.\n\n"
            "That asymmetry is why the answer to 'should I just buy the pass' isn't "
            "the same for everyone; it depends on how many people are traveling, how "
            "many surcharge parks are on the itinerary, and whether everyone's a "
            "resident or not. Roadfare's fee calculator runs the actual comparison "
            "instead of guessing."
        ),
    },
    {
        "slug": "annual-pass-or-pay-as-you-go",
        "title": "Annual pass or pay as you go: how to decide",
        "body": (
            "The naive version of this question is 'will I visit enough parks to "
            "make the pass worth it.' The real answer also depends on residency and "
            "party size, because the non-resident surcharge changes the math.\n\n"
            "For a US resident, the calculation is simple: add up the standard "
            "entrance fees for every park on the trip, and compare that total to $80. "
            "Most families crack even after two or three parks.\n\n"
            "For a non-resident, every park adds not just an entrance fee but a $100 "
            "per-adult surcharge, so the pay-as-you-go total climbs much faster. But "
            "the pass itself costs more too ($250, and only covers the person it's "
            "issued to), so a solo traveler hits the break-even point sooner than a "
            "family where everyone would need their own pass.\n\n"
            "There's no universal answer, which is the point: it's a real "
            "calculation, not a rule of thumb, and it changes with every added park "
            "or person."
        ),
    },
    {
        "slug": "what-a-road-trip-actually-costs",
        "title": "What actually goes into a road trip's true cost",
        "body": (
            "A nightly campervan rate or a per-park entrance fee is never the whole "
            "story. Roadfare itemises every trip into the same categories, because "
            "each one hides its own surprises.\n\n"
            "Transport covers getting between stops. Lodging and fuel scale with "
            "how many nights and miles the route actually needs, not a flat guess. "
            "Entry fees include both the standard park fee and, where it applies, the "
            "non-resident surcharge. Food is a per-person daily estimate. A 15% "
            "buffer sits on top of all of it, because road trips run over budget more "
            "often than under.\n\n"
            "Rental vehicles hide cost the same way: a quoted nightly rate rarely "
            "mentions the mileage overage charge, the one-time prep fee, or a one-way "
            "drop fee until checkout. The campervan cost calculator exists because "
            "those numbers change the total more than people expect."
        ),
    },
]


class Command(BaseCommand):
    help = "Seed a few first-party explainer pages for /guides."

    def handle(self, *args, **options):
        for page_data in PAGES:
            Page.objects.update_or_create(
                slug=page_data["slug"],
                defaults={
                    "title": page_data["title"],
                    "body": page_data["body"],
                    "published": True,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(PAGES)} guide pages."))
