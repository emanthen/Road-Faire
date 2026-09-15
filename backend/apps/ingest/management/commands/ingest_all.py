"""Run every ingest connector end to end; safely re-runnable.

seed_spots -> ingest_nps -> ingest_ridb, in that order (seed before refresh). Climate
normals need a station map (see load_climate_normals.py) and aren't run automatically
here since no default map exists yet — run that one separately once station IDs are
sourced.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run seed_spots, ingest_nps, and ingest_ridb in order. Idempotent."

    def add_arguments(self, parser):
        parser.add_argument("--mode", choices=["record", "replay"], default="record")

    def handle(self, *args, **options):
        mode = options["mode"]
        self.stdout.write("== seed_spots ==")
        call_command("seed_spots", mode=mode)
        self.stdout.write("== ingest_nps ==")
        call_command("ingest_nps", mode=mode)
        self.stdout.write("== ingest_ridb ==")
        call_command("ingest_ridb", mode=mode)
        self.stdout.write(self.style.SUCCESS("ingest_all complete."))
