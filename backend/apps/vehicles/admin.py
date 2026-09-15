from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.vehicles.models import VehicleClass, VehicleSpec


@admin.register(VehicleClass)
class VehicleClassAdmin(ModelAdmin):
    list_display = ("name",)


@admin.register(VehicleSpec)
class VehicleSpecAdmin(ModelAdmin):
    list_display = ("name", "vehicle_class", "length_ft", "height_ft", "sleeps")
    list_filter = ("vehicle_class",)
