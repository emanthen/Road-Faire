"""Populate FeeSchedule from apps.fees.constants — the auditable admin record mirroring
the hardcoded policy the engine actually computes with (see apps/fees/models.py).
Every row lands with needs_verification=True; scripts/verify_fees.py is what later
flags it for re-check, this command only gets the record in.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.fees import constants
from apps.fees.models import FeeSchedule

ROWS = [
    (FeeSchedule.Key.NONRESIDENT_SURCHARGE, constants.NONRESIDENT_SURCHARGE,
     constants.SURCHARGE_SOURCE_URL),
    (FeeSchedule.Key.ATB_RESIDENT, constants.ATB_RESIDENT, constants.ATB_PASS_SOURCE_URL),
    (FeeSchedule.Key.ATB_NONRESIDENT, constants.ATB_NONRESIDENT, constants.ATB_PASS_SOURCE_URL),
]


class Command(BaseCommand):
    help = "Seed FeeSchedule rows from apps.fees.constants. Flags every row for manual review."

    @transaction.atomic
    def handle(self, *args, **options):
        for key, amount, source_url in ROWS:
            schedule, created = FeeSchedule.objects.get_or_create(
                key=key,
                effective_from=constants.EFFECTIVE_FROM,
                defaults={
                    "amount": amount,
                    "source_url": source_url,
                    "needs_verification": True,
                },
            )
            verb = "Created" if created else "Already exists"
            self.stdout.write(f"{verb}: {schedule}")
