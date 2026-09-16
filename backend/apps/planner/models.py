"""TripRequest, Itinerary, ItineraryDay, ItineraryStop, CostLine, SavedTrip."""

import uuid
from decimal import Decimal

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

    # The pass-vs-pay-as-you-go recommendation (apps.fees.dataclasses.PassRecommendation)
    # — a single logical unit with non-money fields, so it lives here rather than as
    # itemised CostLine rows. total_cost above always reflects pay-as-you-go (the
    # conservative default); these are the "buy the pass and save $X" fields.
    entry_annual_pass_total = MoneyField(default=Decimal("0"))
    entry_pass_cheaper = models.CharField(
        max_length=20,
        choices=[
            ("pay_as_you_go", "Pay as you go"),
            ("annual_pass", "Annual pass"),
            ("tie", "Tie"),
        ],
        default="pay_as_you_go",
    )
    entry_pass_savings = MoneyField(default=Decimal("0"))
    entry_pass_explanation = models.TextField(blank=True)

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
        # Present only on a COMFORT (van) itinerary — the itemised true_cost() lines
        # behind that itinerary's flat `transport` total (apps.vehicles.pricing).
        VAN_BASE = "van_base", "Van — base rate"
        VAN_MILEAGE_OVERAGE = "van_mileage_overage", "Van — mileage overage"
        VAN_PREP_FEE = "van_prep_fee", "Van — prep fee"
        VAN_INSURANCE = "van_insurance", "Van — insurance"
        VAN_ONE_WAY_FEE = "van_one_way_fee", "Van — one-way fee"
        VAN_GENERATOR = "van_generator", "Van — generator"
        VAN_HOOKUP_PREMIUM = "van_hookup_premium", "Van — hookup premium"
        VAN_ADDONS = "van_addons", "Van — add-ons"

    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name="cost_lines")
    category = models.CharField(max_length=20, choices=Category.choices)
    amount = MoneyField()
    # True when `amount` came from a bootstrap assumption rather than a cited
    # RateCard/EIA figure — only ever set on lodging/transport/fuel rows (BUILD_PROMPT
    # C2: "$95-140/night (estimate)" is honest, "$120.00" from the same guess is not).
    is_estimate = models.BooleanField(default=False)
    range_low = MoneyField(null=True, blank=True)
    range_high = MoneyField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.get_category_display()}: {self.amount}"


class RateCard(TimeStampedModel):
    """A cited regional/seasonal lodging or car-rental rate range — what apps.planner's
    flat cost-model constants become once real data exists for a region+month+category.
    Seeded from apps.catalog.SpotCost.campsite_low/high (seed_rate_cards); a category
    with no row here falls back to an uncited assumption band, flagged is_estimate on
    the CostLine it produces (apps.planner.rates.load_rate_range)."""

    class Category(models.TextChoices):
        CAMPSITE = "campsite", "Campsite"
        MOTEL = "motel", "Motel"
        CAR = "car", "Car rental"

    region = models.CharField(max_length=10, help_text="State abbreviation, e.g. 'WY'.")
    month = models.PositiveSmallIntegerField()
    category = models.CharField(max_length=20, choices=Category.choices)
    low = MoneyField()
    high = MoneyField()
    source_url = models.URLField(blank=True)
    verified_at = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["region", "month", "category"],
                name="unique_rate_card_region_month_category",
            )
        ]

    def __str__(self) -> str:
        return f"{self.region} {self.category} (month {self.month}): ${self.low}-${self.high}"


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
