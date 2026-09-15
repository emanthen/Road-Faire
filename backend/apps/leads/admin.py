from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from apps.leads.models import EmailEvent, Lead


class EmailEventInline(TabularInline):
    model = EmailEvent
    extra = 0


@admin.register(Lead)
class LeadAdmin(ModelAdmin):
    list_display = ("email", "source", "honeypot_triggered", "created_at")
    list_filter = ("honeypot_triggered", "source")
    inlines = [EmailEventInline]
