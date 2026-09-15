# Roadfare

US road-trip planning and cost-transparency platform. See `BUILD_PROMPT.md` for product spec and
phase gates, `PROJECT_STRUCTURE.md` for the file-tree contract.

## Local development

This machine has no Docker, so local dev runs natively:

```
# backend
cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py runserver

# frontend
cd frontend
npm install
npm run dev
```

With Docker available, `make up` runs the full stack (Postgres+PostGIS, Redis, Django, Celery
worker/beat, Next.js) per `docker-compose.yml`.

## Status

Phase 1 (skeleton) in progress — see phase gates in `BUILD_PROMPT.md` §8.
