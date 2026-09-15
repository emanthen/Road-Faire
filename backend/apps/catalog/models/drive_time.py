"""DriveTime: origin_code, spot, minutes, miles."""

from django.db import models


class DriveTime(models.Model):
    origin_code = models.CharField(max_length=4)
    spot = models.ForeignKey(
        "catalog.Spot", on_delete=models.CASCADE, related_name="drive_times"
    )
    minutes = models.PositiveIntegerField()
    miles = models.DecimalField(max_digits=6, decimal_places=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["origin_code", "spot"], name="unique_drive_time_origin_spot"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.origin_code} -> {self.spot}: {self.minutes}min"
