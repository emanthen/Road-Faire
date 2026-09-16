"""usd() — the one place a Decimal gets quantized to cents.

BUILD_PROMPT §9: all money is Decimal, never float. Decimal math (division especially —
`total_miles / mpg`) can carry many more than 2 decimal places through the context's default
precision; nothing downstream should ever see that. Every money value returned from
apps.fees and apps.planner.engine is routed through this before it leaves the function.
"""

from decimal import ROUND_HALF_UP, Decimal

CENTS = Decimal("0.01")


def usd(value: Decimal) -> Decimal:
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)
