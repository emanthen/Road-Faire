"""Bridges VehicleSpec rows to the pure true_cost() engine — same pattern as
apps.fees.repository. true_cost() never touches the ORM itself; the view loads a spec
and passes it in.
"""

from apps.vehicles.models import VehicleSpec
from apps.vehicles.pricing import VehicleSpecInput


def load_default_van_spec() -> VehicleSpecInput | None:
    """The cheapest seeded VehicleSpec, as the planner's stand-in "the" van until a
    trip can pick a specific rental class. Returns None when no VehicleSpec row exists
    yet (Block D3 hasn't seeded real rental classes) — callers fall back to their own
    bootstrap default rather than guessing a spec here."""

    spec = VehicleSpec.objects.order_by("base_nightly_rate").first()
    if spec is None:
        return None

    return VehicleSpecInput(
        length_ft=spec.length_ft,
        height_ft=spec.height_ft,
        included_miles_per_night=spec.included_miles_per_night,
        overage_rate_per_mile=spec.overage_rate_per_mile,
        base_nightly_rate=spec.base_nightly_rate,
        prep_fee=spec.prep_fee,
        insurance_per_night=spec.insurance_per_night,
        one_way_fee=spec.one_way_fee,
        generator_rate_per_hour=spec.generator_rate_per_hour,
        hookup_premium_per_night=spec.hookup_premium_per_night,
    )
