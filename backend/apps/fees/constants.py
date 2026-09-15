"""Fee constants (BUILD_PROMPT §4.2). Every number here comes from BUILD_PROMPT §1's own
2026 policy description. No magic numbers anywhere else in apps.fees.

SOURCE_URL below is a placeholder pointing at NPS's general fee-info page, not a citation
for the specific 2026 non-resident surcharge policy — I don't have (and won't guess) the
exact NPS.gov announcement URL. Swap this for the real citation before this leaves Phase 3;
tracked as needs_verification on the seeded FeeSchedule/FeeFreeDay rows.
"""

from datetime import date
from decimal import Decimal

SOURCE_URL = "https://www.nps.gov/aboutus/entrance-fee-prices.htm"
EFFECTIVE_FROM = date(2026, 1, 1)

NONRESIDENT_SURCHARGE = Decimal("100")
SURCHARGE_MIN_AGE = 16

ATB_RESIDENT = Decimal("80")
ATB_NONRESIDENT = Decimal("250")

# Matches the lowercase NPS park-code slugs apps.ingest.seed_spots seeds (Phase 2).
SURCHARGE_PARK_SLUGS = frozenset(
    {"acad", "brca", "ever", "glac", "grca", "grte", "romo", "seki", "yell", "yose", "zion"}
)
