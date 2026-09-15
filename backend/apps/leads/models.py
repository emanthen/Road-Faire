"""Lead, EmailEvent."""

from django.db import models


class Lead(models.Model):
    email = models.EmailField()
    source = models.CharField(max_length=100, blank=True)
    honeypot_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email


class EmailEvent(models.Model):
    class EventType(models.TextChoices):
        WELCOME_SENT = "welcome_sent", "Welcome sent"
        OPENED = "opened", "Opened"
        CLICKED = "clicked", "Clicked"

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    occurred_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.get_event_type_display()} — {self.lead}"
