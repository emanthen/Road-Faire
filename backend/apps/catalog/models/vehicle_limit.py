"""VehicleLimit: max_length_ft, max_height_ft, max_weight_lb, effective_from,
applies_to_roads[]."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.core.models import VerifiableModel


class VehicleLimit(VerifiableModel):
    spot = models.ForeignKey(
        "catalog.Spot", on_delete=models.CASCADE, related_name="vehicle_limits"
    )
    max_length_ft = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_height_ft = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_weight_lb = models.PositiveIntegerField(null=True, blank=True)
    effective_from = models.DateField(null=True, blank=True)
    applies_to_roads = ArrayField(models.CharField(max_length=100), default=list, blank=True)

    def __str__(self) -> str:
        return f"Vehicle limit — {self.spot}"
