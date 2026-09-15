"""Spot: slug, geom(Point), type, min_days, vibe_tags, nearest_airports, blurb,
is_manually_verified."""

from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.catalog.managers import SpotQuerySet
from apps.core.models import SluggedModel, TimeStampedModel, VerifiableModel


class Spot(SluggedModel, VerifiableModel, TimeStampedModel):
    class SpotType(models.TextChoices):
        NATIONAL_PARK = "national_park", "National park"
        STATE_PARK = "state_park", "State park"
        MONUMENT = "monument", "National monument"
        FOREST = "forest", "National forest"
        OTHER = "other", "Other"

    name = models.CharField(max_length=200)
    state = models.ForeignKey(
        "catalog.State", on_delete=models.PROTECT, related_name="spots"
    )
    type = models.CharField(max_length=20, choices=SpotType.choices)
    geom = gis_models.PointField(geography=True)
    min_days = models.PositiveSmallIntegerField(default=2)
    vibe_tags = ArrayField(models.CharField(max_length=40), default=list, blank=True)
    nearest_airports = ArrayField(models.CharField(max_length=4), default=list, blank=True)
    blurb = models.TextField(blank=True)
    elevation_ft = models.PositiveIntegerField(null=True, blank=True)
    best_time_to_visit = models.CharField(max_length=300, blank=True)
    highlights = models.TextField(
        blank=True, help_text="What a visitor will actually see there."
    )
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    contact_phone = models.CharField(
        max_length=20, blank=True, help_text="Official visitor center number."
    )

    objects = SpotQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
