from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.core.admin import VerifiableModelAdmin
from apps.fees.models import FeeFreeDay, FeeSchedule


@admin.register(FeeSchedule)
class FeeScheduleAdmin(VerifiableModelAdmin):
    list_display = ("key", "amount", "effective_from", "effective_to", "verified_at")
    list_filter = ("key", *VerifiableModelAdmin.list_filter)


@admin.register(FeeFreeDay)
class FeeFreeDayAdmin(ModelAdmin):
    list_display = ("date", "note")
