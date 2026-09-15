"""CachedPropertyMixin, SoftDeleteQuerySet — shared model/queryset mixins."""

from django.db import models
from django.utils import timezone


class CachedPropertyMixin:
    """Marker mixin for models that use functools.cached_property for derived fields."""


class SoftDeleteQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def delete(self):
        return self.update(deleted_at=timezone.now())
