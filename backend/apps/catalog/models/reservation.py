"""ReservationRule: kind(timed_entry|vehicle|permit|shuttle|lottery), season_start/end,
window_start/end, booking_url, processing_fee, notes, verified_at."""

from django.db import models

from apps.core.fields import MoneyField
from apps.core.models import VerifiableModel


class ReservationRule(VerifiableModel):
    class Kind(models.TextChoices):
        TIMED_ENTRY = "timed_entry", "Timed entry"
        VEHICLE = "vehicle", "Vehicle reservation"
        PERMIT = "permit", "Permit"
        SHUTTLE = "shuttle", "Shuttle ticket"
        LOTTERY = "lottery", "Lottery"

    spot = models.ForeignKey(
        "catalog.Spot", on_delete=models.CASCADE, related_name="reservation_rules"
    )
    kind = models.CharField(max_length=20, choices=Kind.choices)
    season_start = models.DateField(null=True, blank=True)
    season_end = models.DateField(null=True, blank=True)
    window_start = models.TimeField(null=True, blank=True)
    window_end = models.TimeField(null=True, blank=True)
    booking_url = models.URLField(blank=True)
    processing_fee = MoneyField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.get_kind_display()} — {self.spot}"
