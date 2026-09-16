"""Async plan generation for slow requests — apps.planner.views.create_plan_async
creates a PENDING TripRequest row and enqueues generate_plan_async; this moves it
through RUNNING to DONE or FAILED so GET /api/plan/<id> has something to poll."""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def generate_plan_async(trip_request_id: int) -> None:
    from apps.planner.models import TripRequest as TripRequestModel
    from apps.planner.views import _engine_request_from_model, generate_options, persist_itineraries

    db_request = TripRequestModel.objects.get(id=trip_request_id)
    db_request.status = TripRequestModel.Status.RUNNING
    db_request.save(update_fields=["status"])

    try:
        engine_request = _engine_request_from_model(db_request)
        options = generate_options(engine_request)
    except Exception:
        logger.exception("Plan generation failed for TripRequest %s", trip_request_id)
        db_request.status = TripRequestModel.Status.FAILED
        db_request.save(update_fields=["status"])
        return

    if not options:
        db_request.status = TripRequestModel.Status.FAILED
        db_request.save(update_fields=["status"])
        return

    persist_itineraries(db_request, options)
    db_request.status = TripRequestModel.Status.DONE
    db_request.save(update_fields=["status"])
