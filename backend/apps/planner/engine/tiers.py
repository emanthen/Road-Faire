"""LEAN / BALANCED / COMFORT presets.

BUILD_PROMPT names the three tiers but not their exact composition — this is a design
call, stated plainly rather than buried: LEAN = car + tent, self-cook. BALANCED = car +
motel, mixed. COMFORT = van + motel, restaurant.
"""

from dataclasses import dataclass
from typing import Literal

from apps.fees.dataclasses import FeeRates
from apps.planner.engine.types import Loop, TripOption, TripRequest


@dataclass(frozen=True)
class TierPreset:
    name: Literal["LEAN", "BALANCED", "COMFORT"]
    vehicle: Literal["car", "van"]
    lodging: Literal["campsite", "motel", "mixed"]
    food_tier: Literal["self_cook", "mixed", "restaurant"]


LEAN = TierPreset(name="LEAN", vehicle="car", lodging="campsite", food_tier="self_cook")
BALANCED = TierPreset(name="BALANCED", vehicle="car", lodging="motel", food_tier="mixed")
COMFORT = TierPreset(name="COMFORT", vehicle="van", lodging="motel", food_tier="restaurant")

ALL_TIERS = (LEAN, BALANCED, COMFORT)


def cost_all_tiers(
    loop: Loop, request: TripRequest, rates: FeeRates | None = None
) -> list[TripOption]:
    """Returns exactly 3 TripOptions for `loop` — one per tier preset."""
    from apps.planner.engine.costing import cost_loop

    return [
        TripOption(tier=preset.name, loop=loop, cost=cost_loop(loop, request, preset, rates))
        for preset in ALL_TIERS
    ]
