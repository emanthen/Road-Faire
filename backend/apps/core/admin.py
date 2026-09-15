from django.contrib import admin
from unfold.admin import ModelAdmin


class VerifiableModelAdmin(ModelAdmin):
    readonly_fields: tuple[str, ...] = ("verified_at",)
    list_display: tuple[str, ...] = (
        "__str__",
        "verified_at",
        "is_manually_verified",
        "needs_verification",
    )
    list_filter: tuple[str, ...] = ("is_manually_verified", "needs_verification")

    @admin.action(description="Mark selected as manually verified")
    def mark_verified(self, request, queryset):
        from django.utils import timezone

        queryset.update(is_manually_verified=True, verified_at=timezone.now().date())

    actions = ["mark_verified"]
