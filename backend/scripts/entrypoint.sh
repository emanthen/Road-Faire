#!/bin/sh
set -e

python scripts/wait_for_db.py

if [ "$1" = "celery" ]; then
    exec "$@"
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
