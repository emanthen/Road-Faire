"""Partner, Offer, Click, Conversion (BUILD_PROMPT §7)."""

import uuid

from django.db import models

from apps.core.fields import MoneyField
from apps.core.models import TimeStampedModel, VerifiableModel


class Partner(VerifiableModel):
    """A real business we link out to. VerifiableModel because "this business exists,
    at this URL, serving this area" is exactly the kind of fact that goes stale —
    same discipline as Spot/SpotCost, not just money-specific."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    service_area = models.CharField(
        max_length=100, blank=True, help_text="e.g. 'Chicago, IL' — free text, not a Spot."
    )
    contact_phone = models.CharField(max_length=20, blank=True)
    terms_note = models.CharField(
        max_length=300, blank=True, help_text="One verified real policy detail, not full ToS text."
    )
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    rating_count = models.PositiveIntegerField(null=True, blank=True)
    rating_source = models.CharField(
        max_length=40, blank=True, help_text="Where the rating came from, e.g. 'Yelp'."
    )
    rating_url = models.URLField(
        blank=True, help_text="Link to the rating page — a different source than source_url."
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Offer(TimeStampedModel):
    class Category(models.TextChoices):
        CAMPERVAN = "campervan", "Campervan"
        CAR = "car", "Car"
        HOTEL = "hotel", "Hotel"
        CAMPSITE = "campsite", "Campsite"
        ACTIVITY = "activity", "Activity"
        INSURANCE = "insurance", "Insurance"
        BICYCLE = "bicycle", "Bicycle rental"
        CAMPING_GEAR = "camping_gear", "Camping gear rental"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="offers")
    category = models.CharField(max_length=20, choices=Category.choices)
    base_url = models.URLField()
    tracking_params = models.JSONField(default=dict, blank=True)
    commission_note = models.CharField(max_length=200, blank=True)
    description = models.CharField(
        max_length=200, blank=True, help_text="What this offer actually is, e.g. vehicle sizes."
    )
    price_note = models.CharField(
        max_length=100, blank=True, help_text="A real, sourced starting price, e.g. 'From $99/day'."
    )

    def __str__(self) -> str:
        return f"{self.partner} — {self.get_category_display()}"


class Click(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="clicks")
    spot = models.ForeignKey(
        "catalog.Spot", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    session_key = models.CharField(max_length=100)
    referrer = models.CharField(max_length=500, blank=True)
    utm = models.JSONField(default=dict, blank=True)
    is_bot = models.BooleanField(
        default=False, help_text="User-Agent matched a known bot/crawler signature."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Click on {self.offer} @ {self.created_at:%Y-%m-%d %H:%M}"


class Conversion(models.Model):
    """Commission confirmation — mostly a placeholder until a partner's postback/webhook
    exists (not this phase)."""

    click = models.OneToOneField(Click, on_delete=models.CASCADE, related_name="conversion")
    amount = MoneyField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Conversion for {self.click}"
