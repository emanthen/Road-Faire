from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.content.models import FAQ, ChangeLogEntry, Page, SiteSettings


@admin.register(Page)
class PageAdmin(ModelAdmin):
    list_display = ("title", "slug", "published", "updated_at")
    list_filter = ("published",)
    search_fields = ("title", "slug")
    fieldsets = (
        (None, {"fields": ("title", "slug", "published")}),
        ("Content", {"fields": ("body",)}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )


@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    list_display = ("question", "order")


@admin.register(ChangeLogEntry)
class ChangeLogEntryAdmin(ModelAdmin):
    list_display = ("changed_at", "description", "source_url")


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
