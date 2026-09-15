"""TimeStampedModel, SluggedModel, VerifiableModel — shared abstract base models."""

from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SluggedModel(models.Model):
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        abstract = True


class VerifiableModel(models.Model):
    """Fields for data that must be traceable to a cited source (BUILD_PROMPT §0 rule 3)."""

    source_url = models.URLField(blank=True)
    verified_at = models.DateField(null=True, blank=True)
    is_manually_verified = models.BooleanField(default=False)
    needs_verification = models.BooleanField(default=False)

    class Meta:
        abstract = True
