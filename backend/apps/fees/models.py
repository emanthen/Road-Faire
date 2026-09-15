"""FeeSchedule (versioned, effective_from/to), FeeFreeDay.

Neither is read by engine.py — the engine stays pure per BUILD_PROMPT §4.2 ("no ORM
calls inside the math"). These exist as the admin-editable, auditable record of the
policy constants.py currently hardcodes, and as the source scripts/verify_fees.py
checks for staleness.
"""

from django.db import models

from apps.core.models import TimeStampedModel, VerifiableModel


class FeeSchedule(VerifiableModel, TimeStampedModel):
    """One versioned policy value (e.g. "nonresident_surcharge" = $100), auditable
    separately from the constants.py fallback the engine actually computes with."""

    class Key(models.TextChoices):
        NONRESIDENT_SURCHARGE = "nonresident_surcharge", "Non-resident surcharge (per adult)"
        ATB_RESIDENT = "atb_resident", "America the Beautiful pass — resident"
        ATB_NONRESIDENT = "atb_nonresident", "America the Beautiful pass — non-resident"

    key = models.CharField(max_length=40, choices=Key.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-effective_from"]

    def __str__(self) -> str:
        return f"{self.get_key_display()}: ${self.amount} from {self.effective_from}"


class FeeFreeDay(models.Model):
    """A 2026 fee-free date. US-residents-only and never waives the non-resident
    surcharge (BUILD_PROMPT §4.2) — apps.fees.engine doesn't consult this at all."""

    date = models.DateField(unique=True)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self) -> str:
        return self.date.isoformat()
