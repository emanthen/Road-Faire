"""RateRange, load_rate_range() — bridges RateCard to the pure costing engine, same
one-ORM-call-at-the-view-layer pattern as apps.fees.repository / apps.vehicles.repository.

A region+month+category with a real RateCard row (seeded from cited SpotCost data, or
later from a human-entered figure) returns that row's range, is_estimate=False. Anything
else falls back to a fixed assumption band — a range, not a fabricated point value, but
still a guess — flagged is_estimate=True.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class RateRange:
    low: Decimal
    high: Decimal
    is_estimate: bool
    source_url: str | None = None

    @property
    def midpoint(self) -> Decimal:
        return (self.low + self.high) / 2


# Bootstrap bands — same status as the old flat CAMPSITE_NIGHTLY_RATE/MOTEL_NIGHTLY_RATE/
# CAR_DAILY_RATE constants (a cost-model assumption, not a cited fact), just expressed
# honestly as a range instead of false single-dollar precision. Used whenever no
# RateCard row exists for a region+month+category yet.
FALLBACK_BANDS: dict[str, RateRange] = {
    "campsite": RateRange(low=Decimal("25"), high=Decimal("35"), is_estimate=True),
    "motel": RateRange(low=Decimal("90"), high=Decimal("130"), is_estimate=True),
    "car": RateRange(low=Decimal("55"), high=Decimal("75"), is_estimate=True),
}


def load_rate_range(region: str, month: int, category: str) -> RateRange:
    from apps.planner.models import RateCard  # local import — only this function touches the ORM

    row = (
        RateCard.objects.filter(region=region, month=month, category=category).first()
        if region
        else None
    )
    if row is not None:
        return RateRange(
            low=row.low, high=row.high, is_estimate=False, source_url=row.source_url or None
        )
    return FALLBACK_BANDS[category]
