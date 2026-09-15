"""SpotAmenity: campervan-relevant points near a spot (dump stations, potable water)
sourced from OpenStreetMap/Overpass — no API key, no citation-guessing, ODbL-licensed."""

from django.contrib.gis.db import models as gis_models
from django.db import models

from apps.core.models import VerifiableModel


class SpotAmenity(VerifiableModel):
    class Kind(models.TextChoices):
        DUMP_STATION = "dump_station", "Dump station"
        WATER = "water", "Potable water"

    spot = models.ForeignKey(
        "catalog.Spot", on_delete=models.CASCADE, related_name="amenities"
    )
    kind = models.CharField(max_length=20, choices=Kind.choices)
    geom = gis_models.PointField(geography=True)

    def __str__(self) -> str:
        return f"{self.get_kind_display()} near {self.spot}"
