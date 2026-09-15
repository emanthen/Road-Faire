.PHONY: up down build sh test lint migrate seed fees-audit

up:        ; docker compose up
down:      ; docker compose down -v
build:     ; docker compose build --no-cache
sh:        ; docker compose exec backend bash
migrate:   ; docker compose exec backend python manage.py migrate
seed:      ; docker compose exec backend python manage.py seed_spots && docker compose exec backend python manage.py ingest_all
test:      ; docker compose exec backend pytest -q --cov=apps --cov-report=term-missing
lint:      ; docker compose exec backend ruff check . && docker compose exec backend mypy apps
e2e:       ; cd frontend && npx playwright test
fees-audit:; docker compose exec backend python scripts/verify_fees.py
