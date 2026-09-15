"""Inline editing, "mark verified" bulk action."""

from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline, TabularInline

from apps.catalog.models import (
    Activity,
    ClimateNormal,
    CrowdIndex,
    DriveTime,
    Photo,
    Region,
    ReservationRule,
    Spot,
    SpotAmenity,
    SpotCost,
    State,
    VehicleLimit,
)
from apps.core.admin import VerifiableModelAdmin


class SpotCostInline(StackedInline):
    model = SpotCost
    extra = 0


class ReservationRuleInline(TabularInline):
    model = ReservationRule
    extra = 0


class VehicleLimitInline(TabularInline):
    model = VehicleLimit
    extra = 0


class PhotoInline(TabularInline):
    model = Photo
    extra = 1
    fields = ("s3_key", "alt_text", "caption", "credit", "license", "is_primary", "sort_order")


@admin.register(Spot)
class SpotAdmin(VerifiableModelAdmin):
    list_display = ("name", "state", "type", "verified_at", "is_manually_verified")
    list_filter = ("type", "state", *VerifiableModelAdmin.list_filter)
    search_fields = ("name", "slug")
    inlines = [PhotoInline, SpotCostInline, ReservationRuleInline, VehicleLimitInline]
    fieldsets = (
        (None, {"fields": ("name", "slug", "state", "type", "min_days", "vibe_tags")}),
        ("Content", {"fields": ("blurb", "highlights", "elevation_ft", "best_time_to_visit")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
        ("Location", {"fields": ("geom", "nearest_airports")}),
        (
            "Verification",
            {"fields": ("source_url", "verified_at", "is_manually_verified", "needs_verification")},
        ),
    )


@admin.register(Region)
class RegionAdmin(ModelAdmin):
    list_display = ("name",)


@admin.register(State)
class StateAdmin(ModelAdmin):
    list_display = ("name", "abbreviation", "region")
    list_filter = ("region",)


@admin.register(ClimateNormal)
class ClimateNormalAdmin(ModelAdmin):
    pass


@admin.register(CrowdIndex)
class CrowdIndexAdmin(ModelAdmin):
    pass


@admin.register(Activity)
class ActivityAdmin(ModelAdmin):
    pass


@admin.register(DriveTime)
class DriveTimeAdmin(ModelAdmin):
    pass


@admin.register(SpotAmenity)
class SpotAmenityAdmin(VerifiableModelAdmin):
    pass
