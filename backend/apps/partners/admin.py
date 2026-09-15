from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.core.admin import VerifiableModelAdmin
from apps.partners.models import Click, Conversion, Offer, Partner


@admin.register(Partner)
class PartnerAdmin(VerifiableModelAdmin):
    list_display = ("name", "slug", "service_area", "verified_at")
    list_filter = ("service_area", *VerifiableModelAdmin.list_filter)


@admin.register(Offer)
class OfferAdmin(ModelAdmin):
    list_display = ("partner", "category", "commission_note")
    list_filter = ("category", "partner")


@admin.register(Click)
class ClickAdmin(ModelAdmin):
    list_display = ("offer", "spot", "session_key", "created_at")
    list_filter = ("offer",)
    readonly_fields = ("offer", "spot", "session_key", "referrer", "utm", "created_at")

    def has_add_permission(self, request):
        return False


@admin.register(Conversion)
class ConversionAdmin(ModelAdmin):
    list_display = ("click", "amount", "confirmed_at")
    readonly_fields = ("click", "amount", "confirmed_at")

    def has_add_permission(self, request):
        return False
