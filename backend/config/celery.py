import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("roadfare")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "nps-daily": {"task": "apps.ingest.tasks.nps_daily", "schedule": 86400.0},
    "ridb-daily": {"task": "apps.ingest.tasks.ridb_daily", "schedule": 86400.0},
    "places-monthly": {"task": "apps.ingest.tasks.places_monthly", "schedule": 2592000.0},
    "warm-weather-cache-hourly": {
        "task": "apps.weather.tasks.warm_top_spots_cache",
        "schedule": 3600.0,
    },
    "verify-fee-sources-weekly": {
        "task": "apps.fees.tasks.verify_fee_sources_weekly",
        "schedule": 604800.0,
    },
}
