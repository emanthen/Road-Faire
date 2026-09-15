"""ClimateNormal: spot, month, high_f, low_f, precip_in, snow_in (NOAA 1991-2020)."""

from django.db import models


class ClimateNormal(models.Model):
    spot = models.ForeignKey(
        "catalog.Spot", on_delete=models.CASCADE, related_name="climate_normals"
    )
    month = models.PositiveSmallIntegerField()
    high_f = models.DecimalField(max_digits=5, decimal_places=1)
    low_f = models.DecimalField(max_digits=5, decimal_places=1)
    precip_in = models.DecimalField(max_digits=5, decimal_places=2)
    snow_in = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["spot", "month"], name="unique_climate_normal_month"),
            models.CheckConstraint(
                condition=models.Q(month__gte=1) & models.Q(month__lte=12),
                name="climate_normal_month_range",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.spot} — month {self.month}"
