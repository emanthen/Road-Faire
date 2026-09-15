from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from apps.planner.models import (
    CostLine,
    Itinerary,
    ItineraryDay,
    ItineraryStop,
    SavedTrip,
    TripRequest,
)


class ItineraryStopInline(TabularInline):
    model = ItineraryStop
    extra = 0


class ItineraryDayInline(TabularInline):
    model = ItineraryDay
    extra = 0
    show_change_link = True


class CostLineInline(TabularInline):
    model = CostLine
    extra = 0


@admin.register(TripRequest)
class TripRequestAdmin(ModelAdmin):
    list_display = (
        "origin_airport",
        "start_date",
        "end_date",
        "adults",
        "children",
        "vehicle_pref",
        "is_featured",
    )
    list_filter = ("vehicle_pref", "is_us_resident", "is_featured")
    search_fields = ("origin_airport", "public_id")


@admin.register(Itinerary)
class ItineraryAdmin(ModelAdmin):
    list_display = ("trip_request", "tier", "total_cost", "total_miles", "total_days")
    list_filter = ("tier",)
    inlines = [ItineraryDayInline, CostLineInline]


@admin.register(ItineraryDay)
class ItineraryDayAdmin(ModelAdmin):
    list_display = ("itinerary", "day_number")
    inlines = [ItineraryStopInline]


@admin.register(SavedTrip)
class SavedTripAdmin(ModelAdmin):
    list_display = ("itinerary", "user", "session_key", "created_at")
    list_filter = ("created_at",)
    readonly_fields = ("itinerary", "session_key", "user", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False
