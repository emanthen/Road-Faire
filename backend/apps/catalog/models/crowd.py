"""CrowdIndex: spot, month, score 0-100."""

from django.db import models


class CrowdIndex(models.Model):
    spot = models.ForeignKey(
        "catalog.Spot", on_delete=models.CASCADE, related_name="crowd_indexes"
    )
    month = models.PositiveSmallIntegerField()
    score = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["spot", "month"], name="unique_crowd_index_month"),
            models.CheckConstraint(
                condition=models.Q(month__gte=1) & models.Q(month__lte=12),
                name="crowd_index_month_range",
            ),
            models.CheckConstraint(
                condition=models.Q(score__gte=0) & models.Q(score__lte=100),
                name="crowd_index_score_range",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.spot} — month {self.month}: {self.score}"
