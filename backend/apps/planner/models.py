"""TripRequest, Itinerary, ItineraryDay, ItineraryStop, CostLine, SavedTrip."""

import uuid

from django.conf import settings
from django.db import models

from apps.core.fields import MoneyField
from apps.core.models import TimeStampedModel


class TripRequest(TimeStampedModel):
    """A DB record of a submitted planning request — the persisted counterpart to
    apps.planner.engine.types.TripRequest."""

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    origin_airport = models.CharField(max_length=4)
    start_date = models.DateField()
    end_date = models.DateField()
    adults = models.PositiveSmallIntegerField()
    children = models.PositiveSmallIntegerField(default=0)
    budget_usd = MoneyField()
    is_us_resident = models.BooleanField()
    vehicle_pref = models.CharField(max_length=10, choices=[("van", "Van"), ("car", "Car")])
    vibe_tags = models.JSONField(default=list, blank=True)
    max_drive_hours_per_day = models.DecimalField(max_digits=4, decimal_places=1)
    is_featured = models.BooleanField(
        default=False, help_text="Shown on /trips as a curated example itinerary."
    )

    def __str__(self) -> str:
        return f"TripRequest from {self.origin_airport} ({self.start_date})"


class Itinerary(TimeStampedModel):
    trip_request = models.ForeignKey(
        TripRequest, on_delete=models.CASCADE, related_name="itineraries"
    )
    tier = models.CharField(
        max_length=10,
        choices=[("LEAN", "Lean"), ("BALANCED", "Balanced"), ("COMFORT", "Comfort")],
    )
    total_cost = MoneyField()
    total_miles = models.DecimalField(max_digits=8, decimal_places=1)
    total_days = models.PositiveSmallIntegerField()

    def __str__(self) -> str:
        return f"{self.tier} itinerary for {self.trip_request}"


class ItineraryDay(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name="days")
    day_number = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["day_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["itinerary", "day_number"], name="unique_itinerary_day_number"
            )
        ]

    def __str__(self) -> str:
        return f"Day {self.day_number} of {self.itinerary}"


class ItineraryStop(models.Model):
    day = models.ForeignKey(ItineraryDay, on_delete=models.CASCADE, related_name="stops")
    spot = models.ForeignKey("catalog.Spot", on_delete=models.PROTECT, related_name="+")
    nights = models.PositiveSmallIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.spot} on {self.day}"


class CostLine(models.Model):
    """One line item within an Itinerary's cost breakdown — the persisted counterpart
    to apps.planner.engine.types.CostBreakdown's fields."""

    class Category(models.TextChoices):
        TRANSPORT = "transport", "Transport"
        LODGING = "lodging", "Lodging"
        ENTRY = "entry", "Entry fees"
        FUEL = "fuel", "Fuel"
        FOOD = "food", "Food"
        ACTIVITIES = "activities", "Activities"
        BUFFER = "buffer", "Buffer"

    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name="cost_lines")
    category = models.CharField(max_length=20, choices=Category.choices)
    amount = MoneyField()

    def __str__(self) -> str:
        return f"{self.get_category_display()}: {self.amount}"


class SavedTrip(TimeStampedModel):
    """Anonymous saves are keyed by session_key; a logged-in save also records the
    user so it survives across sessions/devices. Both can be set on the same row —
    if a visitor saves anonymously and later logs in, the row isn't re-owned
    retroactively (no session-to-user migration on login), it just stays anonymous."""

    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name="saves")
    session_key = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="saved_trips",
    )

    def __str__(self) -> str:
        return f"Saved {self.itinerary}"
