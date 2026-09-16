"""generate_narrative — the numeral assertion, and the template fallback on any failure.

No ANTHROPIC_API_KEY is configured in this environment, so the live Claude call itself
is never exercised here — only the surrounding contract: what happens on a hallucinated
number, an API error, and a missing key, all via a mocked client.
"""

from unittest.mock import MagicMock, patch

from apps.planner.narrative import NarrativeInput, generate_narrative

PAYLOAD = NarrativeInput(
    tier="LEAN",
    destinations=["Yellowstone", "Grand Teton"],
    days="3",
    total_miles="240",
    total_cost="$1,265.46",
    pass_recommendation="Buying two non-resident passes saves $100.",
)


def _fake_text_response(text: str) -> MagicMock:
    block = MagicMock(type="text", text=text)
    return MagicMock(content=[block])


def test_no_api_key_uses_the_template_fallback():
    with patch("apps.planner.narrative.settings.ANTHROPIC_API_KEY", ""):
        text = generate_narrative(PAYLOAD)

    assert "3" in text
    assert "240" in text
    assert "$1,265.46" in text


def test_valid_model_output_with_only_payload_numbers_is_returned_verbatim():
    model_text = "A 3-day loop through Yellowstone and Grand Teton, 240 miles, $1,265.46 total."
    with (
        patch("apps.planner.narrative.settings.ANTHROPIC_API_KEY", "test-key"),
        patch("apps.planner.narrative.anthropic.Anthropic") as mock_client_cls,
    ):
        mock_client_cls.return_value.messages.create.return_value = _fake_text_response(
            model_text
        )
        text = generate_narrative(PAYLOAD)

    assert text == model_text


def test_hallucinated_number_falls_back_to_the_template():
    model_text = "A 3-day loop covering 999 miles for $1,265.46 total."  # 999 not in payload
    with (
        patch("apps.planner.narrative.settings.ANTHROPIC_API_KEY", "test-key"),
        patch("apps.planner.narrative.anthropic.Anthropic") as mock_client_cls,
    ):
        mock_client_cls.return_value.messages.create.return_value = _fake_text_response(
            model_text
        )
        text = generate_narrative(PAYLOAD)

    assert text != model_text
    assert "999" not in text
    assert "240" in text  # the template, built from the real payload


def test_api_error_falls_back_to_the_template():
    with (
        patch("apps.planner.narrative.settings.ANTHROPIC_API_KEY", "test-key"),
        patch("apps.planner.narrative.anthropic.Anthropic") as mock_client_cls,
    ):
        mock_client_cls.return_value.messages.create.side_effect = ConnectionError("down")
        text = generate_narrative(PAYLOAD)

    assert "$1,265.46" in text


def test_template_never_invents_a_pass_recommendation_sentence_when_absent():
    payload = NarrativeInput(
        tier="LEAN", destinations=["Zion"], days="2", total_miles="50",
        total_cost="$400.00", pass_recommendation="",
    )
    with patch("apps.planner.narrative.settings.ANTHROPIC_API_KEY", ""):
        text = generate_narrative(payload)

    assert "Zion" in text
    assert text.endswith("total.")  # nothing appended after — no recommendation clause
