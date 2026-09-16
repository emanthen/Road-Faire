"""Fee constants (BUILD_PROMPT §4.2). No magic numbers anywhere else in apps.fees.

Both source URLs below were fetched and checked against their live page content on
2026-09-16: entrance-fee-prices.htm states the $100 nonresident fee verbatim, naming all
11 parks at "ages 16 and over"; passes.htm states the $80 resident / $250 non-resident
America the Beautiful annual pass prices verbatim. That's an automated confirmation, not
a human sign-off — these rows still carry needs_verification=True in FeeSchedule, for the
Block-D verification-queue screen to route to a person.
"""

from datetime import date
from decimal import Decimal

SURCHARGE_SOURCE_URL = "https://www.nps.gov/aboutus/entrance-fee-prices.htm"
ATB_PASS_SOURCE_URL = "https://www.nps.gov/planyourvisit/passes.htm"
EFFECTIVE_FROM = date(2026, 1, 1)

NONRESIDENT_SURCHARGE = Decimal("100")
SURCHARGE_MIN_AGE = 16

ATB_RESIDENT = Decimal("80")
ATB_NONRESIDENT = Decimal("250")

# Matches the lowercase NPS park-code slugs apps.ingest.seed_spots seeds (Phase 2).
SURCHARGE_PARK_SLUGS = frozenset(
    {"acad", "brca", "ever", "glac", "grca", "grte", "romo", "seki", "yell", "yose", "zion"}
)
