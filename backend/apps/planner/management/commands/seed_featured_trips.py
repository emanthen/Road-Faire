"""Generate a few real example itineraries against the demo catalog and mark them
featured, so /trips has something to show. Runs the actual planner pipeline
(candidate_spots -> build_loops -> build_trip_options) — these are real computed
numbers against [DEMO DATA] spots, not hand-typed figures. Requires seed_demo_data to
have run first.
"""

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError

from apps.planner.engine.budget import build_trip_options
from apps.planner.engine.candidates import candidate_spots
from apps.planner.engine.clustering import build_loops
from apps.planner.engine.types import TripRequest as EngineTripRequest
from apps.planner.models import TripRequest as TripRequestModel
from apps.planner.views import _persist

# origin_airport, start_date, end_date, max_drive_hours_per_day
EXAMPLES = [
    ("JAC", date(2026, 7, 1), date(2026, 7, 6), Decimal("5.0")),
    ("LAS", date(2026, 8, 1), date(2026, 8, 8), Decimal("5.0")),
    ("DEN", date(2026, 6, 1), date(2026, 6, 5), Decimal("5.0")),
]


class Command(BaseCommand):
    help = "Generate featured example trips against the demo catalog for /trips."

    def handle(self, *args, **options):
        created = 0
        for origin_airport, start_date, end_date, max_drive_hours in EXAMPLES:
            engine_request = EngineTripRequest(
                origin_airport=origin_airport,
                start_date=start_date,
                end_date=end_date,
                adults=2,
                children=0,
                budget_usd=Decimal("5000.00"),
                is_us_resident=False,
                vehicle_pref="car",
                vibe_tags=[],
                max_drive_hours_per_day=max_drive_hours,
            )

            try:
                candidates = candidate_spots(
                    engine_request.origin_airport,
                    engine_request.start_date,
                    engine_request.max_drive_hours_per_day,
                    engine_request.days,
                )
            except ValueError as exc:
                raise CommandError(str(exc)) from exc

            loops = build_loops(
                candidates,
                engine_request.origin_airport,
                engine_request.days,
                engine_request.max_drive_hours_per_day,
                engine_request.start_date,
            )
            trip_options = build_trip_options(loops, engine_request)

            if not trip_options:
                self.stderr.write(
                    self.style.WARNING(f"{origin_airport}: no trips found, skipping")
                )
                continue

            db_request = _persist(engine_request, trip_options)
            TripRequestModel.objects.filter(pk=db_request.pk).update(is_featured=True)
            created += 1
            self.stdout.write(f"{origin_airport}: featured trip {db_request.public_id}")

        self.stdout.write(self.style.SUCCESS(f"Created {created} featured trips."))
