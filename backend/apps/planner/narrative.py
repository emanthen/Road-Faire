"""Claude API call — PROSE ONLY, numbers injected, never generated (BUILD_PROMPT §4/C4).

The system prompt forbids the model from writing any digit that isn't already present
in the injected payload; a post-generation assertion re-checks that mechanically (every
\\d+ run in the output must appear somewhere in the payload) and raises if it doesn't —
a hallucinated figure must never reach a user, even a plausible-looking one Claude wrote
with good intentions. Any failure — no API key, a network error, or the assertion
itself — falls back to a template-rendered narrative built from the same payload; a
plan must never fail to render because the LLM did.
"""

import json
import logging
import re
from dataclasses import asdict, dataclass

import anthropic
from django.conf import settings

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-5"
MAX_TOKENS = 1000

SYSTEM_PROMPT = """You are writing a short narrative paragraph introducing one option \
in a road-trip itinerary. You are given a JSON payload of facts about the trip — every \
value is a string, already formatted exactly as it should appear to the reader.

Rules, with no exceptions:
- Every digit you write must come from copying a value in the payload verbatim. Never \
compute, round, convert, or restate a number in a different format than given.
- Never write a digit that does not appear somewhere in the payload's values.
- Write 2-4 sentences. Plain language, sentence case, no exclamation marks, no \
marketing superlatives ("amazing", "unforgettable").
- Describe only what the payload states — do not invent weather, difficulty, opinions, \
or any fact not present in it.
"""


@dataclass(frozen=True)
class NarrativeInput:
    """Every fact the narrative is allowed to mention, already formatted as a display
    string — the model is never given a raw Decimal/int/date it could recompute."""

    tier: str
    destinations: list[str]
    days: str
    total_miles: str
    total_cost: str
    pass_recommendation: str


class NarrativeGenerationError(Exception):
    """The model's output contained a number absent from the input payload, the API
    call failed, or no key is configured — always caught by generate_narrative(),
    never raised past it."""


def generate_narrative(payload: NarrativeInput) -> str:
    try:
        return _generate_via_claude(payload)
    except Exception:
        logger.warning("Narrative generation failed; using template fallback", exc_info=True)
        return _template_narrative(payload)


def _generate_via_claude(payload: NarrativeInput) -> str:
    if not settings.ANTHROPIC_API_KEY:
        raise NarrativeGenerationError("ANTHROPIC_API_KEY not configured")

    payload_json = json.dumps(asdict(payload))

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": payload_json}],
    )
    text = "".join(block.text for block in response.content if block.type == "text")

    _assert_no_hallucinated_numbers(text, payload_json)
    return text


def _assert_no_hallucinated_numbers(text: str, payload_json: str) -> None:
    for number in re.findall(r"\d+", text):
        if number not in payload_json:
            raise NarrativeGenerationError(
                f"model output contained {number!r}, not present in the input payload"
            )


def _template_narrative(payload: NarrativeInput) -> str:
    stops = ", ".join(payload.destinations) if payload.destinations else "your route"
    sentence = (
        f"This {payload.tier.lower()} option covers {stops} over {payload.days} days "
        f"and {payload.total_miles} miles, for {payload.total_cost} total."
    )
    if payload.pass_recommendation:
        sentence += f" {payload.pass_recommendation}"
    return sentence
