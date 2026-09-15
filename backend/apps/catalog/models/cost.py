"""SpotCost: entry_vehicle, entry_person, parking, campsite_low/high, shuttle, source_url,
verified_at."""

from django.db import models

from apps.core.fields import MoneyField
from apps.core.models import VerifiableModel


class SpotCost(VerifiableModel):
    spot = models.OneToOneField(
        "catalog.Spot", on_delete=models.CASCADE, related_name="cost"
    )
    entry_vehicle = MoneyField(null=True, blank=True)
    entry_person = MoneyField(null=True, blank=True)
    parking = MoneyField(null=True, blank=True)
    campsite_low = MoneyField(null=True, blank=True)
    campsite_high = MoneyField(null=True, blank=True)
    shuttle = MoneyField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Cost for {self.spot}"
