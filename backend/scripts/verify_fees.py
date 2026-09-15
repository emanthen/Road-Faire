"""Prints every fee row older than 90 days (BUILD_PROMPT §9 staleness rule).
Exits non-zero when any row is stale, so CI can gate on it."""

import os
import sys
from datetime import date, timedelta
from pathlib import Path

import django

# Running `python scripts/verify_fees.py` puts scripts/ (not the backend root) at
# sys.path[0], so `config.settings.local` can't resolve without this — same fix needed
# in wait_for_db.py, hit there too since neither script is ever run as a package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.db.models import Q  # noqa: E402

from apps.fees.models import FeeSchedule  # noqa: E402

STALE_AFTER_DAYS = 90


def main() -> None:
    cutoff = date.today() - timedelta(days=STALE_AFTER_DAYS)
    stale = FeeSchedule.objects.filter(
        Q(verified_at__isnull=True) | Q(verified_at__lt=cutoff)
    ).order_by("key")

    if not stale.exists():
        print("All fee rows verified within the last 90 days.")
        return

    print(f"{stale.count()} fee row(s) need re-verification (source_url must be re-checked):")
    for row in stale:
        verified = row.verified_at.isoformat() if row.verified_at else "never"
        print(f"  - {row.get_key_display()}: ${row.amount} — last verified {verified}")
        print(f"    source: {row.source_url or '(none)'}")
    sys.exit(1)


if __name__ == "__main__":
    main()
