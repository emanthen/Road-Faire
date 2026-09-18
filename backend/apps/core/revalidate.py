"""Notifies frontend/src/app/api/revalidate when published data changes.

Not itself an ingest client (apps.ingest.clients.base's record/replay fixture pattern
is for pulling external data in, not pushing a notification out), but the same
"never let this optional side call break the actual work" posture as everywhere else
in this app: any failure is caught and logged, never raised — a page staying stale a
little longer beats a save() failing because the frontend was unreachable.
"""

import logging

from django.conf import settings

from apps.core.http import get_session

logger = logging.getLogger(__name__)


def notify_revalidate(kind: str, slug: str) -> None:
    """kind is "spot" or "content" — mirrors frontend/src/app/api/revalidate's
    RevalidateBody.kind, which maps it to the actual Next.js paths to bust."""
    if not settings.REVALIDATE_SECRET:
        return

    url = f"{settings.FRONTEND_BASE_URL}/api/revalidate"
    try:
        response = get_session().post(
            url,
            json={"kind": kind, "slug": slug},
            headers={"x-revalidate-secret": settings.REVALIDATE_SECRET},
            timeout=5,
        )
        response.raise_for_status()
    except Exception:
        logger.warning("Revalidate webhook failed for %s:%s", kind, slug, exc_info=True)
