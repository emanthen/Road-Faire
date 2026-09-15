"""MoneyField (Decimal 10,2), URLSourceField.

BUILD_PROMPT §9: all money is Decimal, never float.
"""

from django.db import models


class MoneyField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_digits", 10)
        kwargs.setdefault("decimal_places", 2)
        super().__init__(*args, **kwargs)


class URLSourceField(models.URLField):
    """A URL field whose value must be a citable source (BUILD_PROMPT §0 rule 3)."""
