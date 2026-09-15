"""Page, FAQ, ChangeLogEntry (what rule changed, when)."""

from django.db import models

from apps.core.models import SluggedModel, TimeStampedModel


class Page(SluggedModel, TimeStampedModel):
    """A static editorial page (guides, about-style content)."""

    title = models.CharField(max_length=200)
    body = models.TextField()
    published = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self) -> str:
        return self.question


class SiteSettings(models.Model):
    """Singleton: the one row of staff-editable branding. Enforced as a singleton in
    admin.py (has_add_permission), not here — a DB-level check would need a raw
    constraint or a fixed pk, more machinery than one admin-panel check needs."""

    site_name = models.CharField(max_length=100, default="Roadfare")
    tagline = models.CharField(max_length=200, blank=True)
    logo_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)

    class Meta:
        verbose_name_plural = "Site settings"

    def __str__(self) -> str:
        return self.site_name


class ChangeLogEntry(models.Model):
    """What rule changed, when — the visible freshness surface BUILD_PROMPT §6 wants
    ("Fees verified..." lines) backed by an actual audit trail, not just a timestamp."""

    description = models.CharField(max_length=300)
    source_url = models.URLField(blank=True)
    changed_at = models.DateField()

    class Meta:
        ordering = ["-changed_at"]
        verbose_name_plural = "Change log entries"

    def __str__(self) -> str:
        return f"{self.changed_at}: {self.description}"
