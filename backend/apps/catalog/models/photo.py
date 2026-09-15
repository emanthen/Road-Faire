"""Photo: source, credit, license, s3_key."""

from django.db import models


class Photo(models.Model):
    spot = models.ForeignKey(
        "catalog.Spot", on_delete=models.CASCADE, related_name="photos"
    )
    source = models.CharField(max_length=100)
    credit = models.CharField(max_length=200, blank=True)
    license = models.CharField(max_length=100, blank=True)
    s3_key = models.CharField(max_length=500)
    alt_text = models.CharField(max_length=300, blank=True)
    caption = models.CharField(max_length=300, blank=True)
    is_primary = models.BooleanField(
        default=False, help_text="The one photo shown before a visitor opens the gallery."
    )
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"Photo for {self.spot}"
