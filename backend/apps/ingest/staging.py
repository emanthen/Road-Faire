"""StagedRecord model — raw payload + diff before promote."""

from django.db import models


class StagedRecord(models.Model):
    """A raw external-API payload, held for diffing against live data before promote()
    applies it. See apps.ingest.promote."""

    source = models.CharField(max_length=50)  # e.g. "nps", "ridb"
    external_id = models.CharField(max_length=100)  # e.g. an NPS park code
    raw_payload = models.JSONField()
    fetched_at = models.DateTimeField(auto_now_add=True)
    promoted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["source", "external_id"])]
        ordering = ["-fetched_at"]

    def __str__(self) -> str:
        return f"{self.source}:{self.external_id} @ {self.fetched_at:%Y-%m-%d}"
