"""VehicleClass, VehicleSpec (length, height, mpg, sleeps, included_miles_per_night,
overage_rate)."""

from django.db import models

from apps.core.fields import MoneyField


class VehicleClass(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class VehicleSpec(models.Model):
    vehicle_class = models.ForeignKey(
        VehicleClass, on_delete=models.PROTECT, related_name="specs"
    )
    name = models.CharField(max_length=100)
    length_ft = models.DecimalField(max_digits=5, decimal_places=2)
    height_ft = models.DecimalField(max_digits=5, decimal_places=2)
    mpg = models.DecimalField(max_digits=4, decimal_places=1)
    sleeps = models.PositiveSmallIntegerField()
    included_miles_per_night = models.PositiveIntegerField()
    overage_rate_per_mile = MoneyField()
    base_nightly_rate = MoneyField()
    prep_fee = MoneyField()
    insurance_per_night = MoneyField()
    one_way_fee = MoneyField()
    generator_rate_per_hour = MoneyField()
    hookup_premium_per_night = MoneyField()

    def __str__(self) -> str:
        return self.name
