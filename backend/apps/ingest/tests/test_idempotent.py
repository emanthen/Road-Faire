"""Re-running ingest_all on a populated DB is a no-op diff.

Needs the DB (Spot/SpotCost creation via seed_spots), so — like every other test that
touches pytest-django's `db` fixture — this can't actually run until PostGIS is
installed on the local Postgres (same blocker as `migrate`, tracked since Phase 1).
Written now, verified once that's unblocked.

Tests _seed_one() directly (the unit seed_spots.Command loops over SEED_PARK_CODES to
call) against the "TEST" fixture rather than running the full 25-park-code command,
since replay fixtures only exist for the synthetic TEST park — the 25 real seed codes
need live "record" mode fixtures pulled from the actual NPS API, which is a data-sourcing
step for the user, not something to fake here.
"""

import pytest

from apps.catalog.models import Spot, SpotCost
from apps.ingest.clients.nps import NPSClient
from apps.ingest.management.commands.seed_spots import Command
from apps.ingest.staging import StagedRecord

pytestmark = pytest.mark.django_db


def test_seeding_same_park_twice_does_not_duplicate():
    command = Command()
    client = NPSClient(mode="replay")

    command._seed_one(client, "TEST")
    command._seed_one(client, "TEST")

    assert Spot.objects.filter(slug="test").count() == 1
    assert SpotCost.objects.filter(spot__slug="test").count() == 1
    # Each run stages its raw payloads regardless — that history is meant to accumulate.
    assert StagedRecord.objects.filter(external_id="TEST").count() == 4


def test_reseeding_does_not_clobber_a_manually_verified_spot():
    command = Command()
    client = NPSClient(mode="replay")

    command._seed_one(client, "TEST")
    spot = Spot.objects.get(slug="test")
    spot.name = "Hand-corrected name"
    spot.is_manually_verified = True
    spot.save()

    command._seed_one(client, "TEST")

    spot.refresh_from_db()
    assert spot.name == "Hand-corrected name"
