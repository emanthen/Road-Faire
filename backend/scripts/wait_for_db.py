"""Blocks until the configured database accepts connections, or exits non-zero after a timeout."""

import os
import sys
import time
from pathlib import Path

import django

# Running `python scripts/wait_for_db.py` puts scripts/ (not the backend root) at
# sys.path[0], so `config.settings.local` can't resolve without this.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.db import connection  # noqa: E402
from django.db.utils import OperationalError  # noqa: E402

MAX_ATTEMPTS = 30
DELAY_SECONDS = 1


def main() -> None:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            connection.ensure_connection()
            print("Database is available.")
            return
        except OperationalError:
            print(f"Database unavailable, attempt {attempt}/{MAX_ATTEMPTS}...")
            time.sleep(DELAY_SECONDS)
    print("Database never became available.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
