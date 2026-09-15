"""Region, State — hierarchy for browse pages."""

from django.db import models


class Region(models.Model):
    """A multi-state area used for browse pages (e.g. "Pacific Northwest")."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=2, unique=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="states")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.abbreviation
