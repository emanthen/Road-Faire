"""Populate RateCard(category="campsite") from apps.catalog.SpotCost.campsite_low/high —
the only rate data that's real and cited today (BUILD_PROMPT C2). One row per state,
applied to all 12 months (no seasonal campsite data exists yet — honest about that,
not fabricated): low = min across that state's spots, high = max.

Leaves motel/car rows unseeded entirely — apps.planner.rates.load_rate_range() falls
back to the uncited assumption band for those until real data exists (Block D3-ish
territory, not invented here).
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import SpotCost
from apps.planner.models import RateCard


class Command(BaseCommand):
    help = "Seed RateCard(campsite) rows from SpotCost.campsite_low/high, aggregated per state."

    @transaction.atomic
    def handle(self, *args, **options):
        by_state: dict[str, list[SpotCost]] = {}
        for cost in SpotCost.objects.select_related("spot__state").filter(
            campsite_low__isnull=False, campsite_high__isnull=False
        ):
            by_state.setdefault(cost.spot.state.abbreviation, []).append(cost)

        if not by_state:
            self.stdout.write("No SpotCost rows have campsite_low/high set — nothing to seed.")
            return

        created = 0
        for region, costs in by_state.items():
            low = min(c.campsite_low for c in costs)
            high = max(c.campsite_high for c in costs)
            for month in range(1, 13):
                _, was_created = RateCard.objects.update_or_create(
                    region=region,
                    month=month,
                    category=RateCard.Category.CAMPSITE,
                    defaults={"low": low, "high": high},
                )
                created += was_created

        self.stdout.write(f"Seeded RateCard(campsite) for {len(by_state)} state(s), "
                           f"{created} new row(s) (12 months each).")
