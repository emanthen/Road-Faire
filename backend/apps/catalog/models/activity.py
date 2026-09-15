"""Activity: trail/tour, distance, elevation, permit_required."""

from django.db import models


class Activity(models.Model):
    class Kind(models.TextChoices):
        TRAIL = "trail", "Trail"
        TOUR = "tour", "Tour"

    spot = models.ForeignKey(
        "catalog.Spot", on_delete=models.CASCADE, related_name="activities"
    )
    name = models.CharField(max_length=200)
    kind = models.CharField(max_length=10, choices=Kind.choices)
    distance_mi = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    elevation_gain_ft = models.PositiveIntegerField(null=True, blank=True)
    permit_required = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name
