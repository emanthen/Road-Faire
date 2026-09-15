"""SpotQuerySet.within_drive_of(), .best_in_month()."""

from django.db import models


class SpotQuerySet(models.QuerySet):
    def within_drive_of(self, origin_code: str, max_minutes: int) -> "SpotQuerySet":
        return self.filter(
            drive_times__origin_code=origin_code,
            drive_times__minutes__lte=max_minutes,
        ).distinct()

    def best_in_month(self, month: int, min_score: int = 60) -> list:
        """Spots scoring >= min_score for `month`, best first.

        month_score() isn't a DB expression (it weighs climate + crowd in Python).
        ponytail: O(n) Python-side scoring of every spot in the queryset, fine at the
        scale of a hand-curated catalog (dozens-hundreds of spots). Upgrade path: precompute
        month_score into a stored/indexed column once the catalog is large enough to matter.
        """
        from apps.catalog.scoring import month_score

        scored = [(spot, month_score(spot, month)) for spot in self]
        scored = [(spot, score) for spot, score in scored if score >= min_score]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [spot for spot, _ in scored]
