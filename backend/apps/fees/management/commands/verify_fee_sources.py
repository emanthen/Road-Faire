"""Re-fetch every FeeSchedule row's source_url and confirm the stored amount still
appears on the live page. This is the automated half of the trust mechanism BUILD_PROMPT
§9 asks for — it does not replace a human clicking "I checked this" (Block D's
verification queue, is_manually_verified), it just tells that queue what's gone stale so
a person isn't the one who has to notice a price changed.

Flags, never silently fixes: a mismatch sets needs_verification=True and is reported, but
the stored amount is never overwritten from what the command scrapes — that's exactly the
"don't blind-overwrite a hand-verified field" rule from BUILD_PROMPT §3.
"""

import sys

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.http import get_session
from apps.fees.models import FeeSchedule


class Command(BaseCommand):
    help = "Re-check every FeeSchedule row's source_url still states the stored amount."

    def handle(self, *args, **options):
        rows = FeeSchedule.objects.exclude(source_url="")
        if not rows.exists():
            self.stdout.write("No FeeSchedule rows have a source_url to check.")
            return

        session = get_session()
        mismatches = []

        # Group by URL — several rows can share one page (both ATB prices live on the
        # same passes.htm), no reason to fetch it twice.
        by_url: dict[str, list[FeeSchedule]] = {}
        for row in rows:
            by_url.setdefault(row.source_url, []).append(row)

        for url, url_rows in by_url.items():
            try:
                response = session.get(url, timeout=10)
                response.raise_for_status()
            except Exception as exc:  # noqa: BLE001 — report and move on, one bad URL shouldn't kill the run
                for row in url_rows:
                    mismatches.append((row, f"fetch failed: {exc}"))
                continue

            page_text = response.text
            for row in url_rows:
                if _amount_present(row.amount, page_text):
                    row.verified_at = timezone.now().date()
                    row.save(update_fields=["verified_at"])
                    self.stdout.write(
                        f"OK: {row.get_key_display()} — ${row.amount} confirmed on {url}"
                    )
                else:
                    row.needs_verification = True
                    row.save(update_fields=["needs_verification"])
                    mismatches.append((row, f"${row.amount} not found on {url}"))

        if mismatches:
            self.stdout.write(self.style.WARNING(f"\n{len(mismatches)} mismatch(es):"))
            for row, reason in mismatches:
                self.stdout.write(f"  - {row.get_key_display()}: {reason}")
            sys.exit(1)


def _amount_present(amount, page_text: str) -> bool:
    """Tolerant match: pages format money as "$100" or "$100.00" — accept either."""
    whole = str(int(amount))
    two_dp = f"{amount:.2f}"
    return whole in page_text or two_dp in page_text
