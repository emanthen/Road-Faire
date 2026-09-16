"""Celery beat: verify_fee_sources_weekly — BUILD_PROMPT §9's staleness mechanism."""

from celery import shared_task
from django.core.management import call_command


@shared_task
def verify_fee_sources_weekly():
    call_command("verify_fee_sources")
